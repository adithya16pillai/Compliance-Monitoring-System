import streamlit as st
import requests
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Compliance Monitor",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("🔍 Compliance Monitoring Dashboard")
    st.markdown("Upload documents and analyze them for compliance violations")
    
    # Display API status
    display_api_status()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload & Analyze", "Document Library", "Compliance Reports", "Rule Management"]
    )
    
    if page == "Upload & Analyze":
        upload_and_analyze_page()
    elif page == "Document Library":
        document_library_page()
    elif page == "Compliance Reports":
        compliance_reports_page()
    elif page == "Rule Management":
        rule_management_page()

def upload_and_analyze_page():
    st.header("📄 Upload & Analyze Document")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT (Max 10MB)"
    )
    
    # Rule selection
    st.subheader("🔧 Select Compliance Rules")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        check_gdpr = st.checkbox("GDPR", value=True)
    with col2:
        check_hipaa = st.checkbox("HIPAA", value=True)
    with col3:
        check_sox = st.checkbox("SOX", value=True)
    
    # Build rule types list
    rule_types = []
    if check_gdpr:
        rule_types.append("GDPR")
    if check_hipaa:
        rule_types.append("HIPAA")
    if check_sox:
        rule_types.append("SOX")
    
    if uploaded_file is not None and st.button("🚀 Upload & Analyze"):
        with st.spinner("Uploading document..."):
            # Upload file
            files = {"file": uploaded_file.getvalue()}
            upload_response = requests.post(
                f"{API_BASE_URL}/upload-document/",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            )
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                document_id = upload_data["document_id"]
                
                st.success(f"✅ Document uploaded successfully! ID: {document_id}")
                
                # Analyze compliance
                with st.spinner("Analyzing compliance..."):
                    analyze_response = requests.post(
                        f"{API_BASE_URL}/analyze-compliance/{document_id}",
                        json={"rule_types": rule_types}
                    )
                    
                    if analyze_response.status_code == 200:
                        analysis_data = analyze_response.json()
                        display_analysis_results(analysis_data)
                    else:
                        st.error(f"❌ Analysis failed: {analyze_response.text}")
            else:
                st.error(f"❌ Upload failed: {upload_response.text}")

def display_analysis_results(analysis_data):
    """Display compliance analysis results"""
    st.header("📊 Analysis Results")
    
    results = analysis_data.get("analysis_results", {})
    summary = results.get("summary", {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Compliance Score",
            f"{summary.get('compliance_score', 0):.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Total Violations", 
            summary.get('total_violations', 0)
        )
    
    with col3:
        st.metric(
            "Total Checks", 
            summary.get('total_checks', 0)
        )
    
    with col4:
        st.metric(
            "High Confidence", 
            summary.get('high_confidence_violations', 0)
        )
    
    # Violations by type chart
    if summary.get('violations_by_type'):
        st.subheader("📈 Violations by Rule Type")
        violations_df = pd.DataFrame(list(summary['violations_by_type'].items()), 
                                   columns=['Rule Type', 'Violations'])
        fig = px.bar(violations_df, x='Rule Type', y='Violations', 
                    title="Compliance Violations by Rule Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Violations by severity
    if summary.get('violations_by_severity'):
        st.subheader("⚠️ Violations by Severity")
        severity_df = pd.DataFrame(list(summary['violations_by_severity'].items()), 
                                 columns=['Severity', 'Count'])
        fig = px.pie(severity_df, values='Count', names='Severity', 
                    title="Violations by Severity Level")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results
    detailed_results = results.get('detailed_results', [])
    if detailed_results:
        st.subheader("🔍 Detailed Violation Results")
        
        violations_only = [r for r in detailed_results if r.get('overall_violation', False)]
        
        if violations_only:
            for i, violation in enumerate(violations_only):
                with st.expander(f"❌ {violation.get('rule_name', 'Unknown Rule')} - {violation.get('severity', 'MEDIUM')} Severity"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Rule Type:** {violation.get('rule_type', 'N/A')}")
                        st.write(f"**Description:** {violation.get('violation_type', 'N/A')}")
                        st.write(f"**Explanation:** {violation.get('llm_explanation', 'No explanation available')}")
                        
                        if violation.get('llm_evidence'):
                            st.write("**Evidence:**")
                            for evidence in violation['llm_evidence']:
                                st.write(f"• {evidence}")
                    
                    with col2:
                        st.metric("Confidence", f"{violation.get('confidence_score', 0):.2f}")
                        st.write(f"**Severity:** {violation.get('severity', 'MEDIUM')}")
        else:
            st.success("✅ No violations found in this document!")
    
    # Download report button
    if st.button("📄 Download Full Report"):
        report_json = json.dumps(analysis_data, indent=2, default=str)
        st.download_button(
            label="Download JSON Report",
            data=report_json,
            file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def document_library_page():
    """Display all uploaded documents with their status"""
    st.header("📚 Document Library")
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents/")
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            
            if documents:
                # Create dataframe for display
                docs_df = pd.DataFrame(documents)
                docs_df['uploaded_at'] = pd.to_datetime(docs_df['uploaded_at'])
                docs_df['file_size_mb'] = (docs_df['file_size'] / (1024*1024)).round(2)
                
                # Display filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    file_type_filter = st.selectbox(
                        "Filter by File Type",
                        ["All"] + list(docs_df['file_type'].unique())
                    )
                
                with col2:
                    date_filter = st.date_input("Filter by Date", value=None)
                
                with col3:
                    if st.button("🔄 Refresh"):
                        st.rerun()
                
                # Apply filters
                filtered_df = docs_df.copy()
                if file_type_filter != "All":
                    filtered_df = filtered_df[filtered_df['file_type'] == file_type_filter]
                
                # Display documents
                for _, doc in filtered_df.iterrows():
                    with st.expander(f"📄 {doc['filename']} ({doc['file_type'].upper()}) - {doc['file_size_mb']} MB"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Document ID:** {doc['id']}")
                            st.write(f"**Uploaded:** {doc['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                            st.write(f"**File Size:** {doc['file_size_mb']} MB")
                            
                            # Get compliance results for this document
                            compliance_response = requests.get(f"{API_BASE_URL}/compliance-results/{doc['id']}")
                            if compliance_response.status_code == 200:
                                compliance_data = compliance_response.json()
                                results = compliance_data.get("results", [])
                                violations = [r for r in results if r.get('is_violation', False)]
                                
                                if violations:
                                    st.error(f"❌ {len(violations)} violations found")
                                    for violation in violations[:3]:  # Show first 3
                                        st.write(f"• {violation.get('rule_type')} - {violation.get('violation_type')}")
                                    if len(violations) > 3:
                                        st.write(f"... and {len(violations) - 3} more")
                                else:
                                    st.success("✅ No violations detected")
                            else:
                                st.info("ℹ️ No analysis results available")
                        
                        with col2:
                            if st.button(f"🔍 Analyze", key=f"analyze_{doc['id']}"):
                                # Redirect to analysis
                                st.session_state.selected_doc_id = doc['id']
                                st.session_state.page = "Upload & Analyze"
                                st.rerun()
                            
                            if st.button(f"📊 View Results", key=f"results_{doc['id']}"):
                                st.session_state.selected_doc_id = doc['id']
                                st.session_state.page = "Compliance Reports"
                                st.rerun()
            else:
                st.info("📭 No documents uploaded yet. Go to 'Upload & Analyze' to get started!")
                
    except requests.RequestException as e:
        st.error(f"❌ Error connecting to API: {str(e)}")

def compliance_reports_page():
    """Display comprehensive compliance reports and analytics"""
    st.header("📊 Compliance Reports & Analytics")
    
    # Document selector
    try:
        response = requests.get(f"{API_BASE_URL}/documents/")
        if response.status_code == 200:
            documents = response.json().get("documents", [])
            
            if documents:
                # Document selection
                doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
                selected_doc = st.selectbox("Select Document for Detailed Report", list(doc_options.keys()))
                
                if selected_doc:
                    doc_id = doc_options[selected_doc]
                    
                    # Get compliance results
                    compliance_response = requests.get(f"{API_BASE_URL}/compliance-results/{doc_id}")
                    
                    if compliance_response.status_code == 200:
                        compliance_data = compliance_response.json()
                        results = compliance_data.get("results", [])
                        
                        if results:
                            # Create results dataframe
                            results_df = pd.DataFrame(results)
                            
                            # Overview metrics
                            st.subheader("📈 Overview")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            violations = results_df[results_df['is_violation'] == True]
                            
                            with col1:
                                compliance_score = ((len(results_df) - len(violations)) / len(results_df)) * 100
                                st.metric("Compliance Score", f"{compliance_score:.1f}%")
                            
                            with col2:
                                st.metric("Total Violations", len(violations))
                            
                            with col3:
                                high_conf = violations[violations['confidence_score'] > 0.7]
                                st.metric("High Confidence", len(high_conf))
                            
                            with col4:
                                avg_confidence = violations['confidence_score'].mean() if len(violations) > 0 else 0
                                st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                            
                            # Charts
                            if len(violations) > 0:
                                # Violations by rule type
                                st.subheader("🔍 Violations by Rule Type")
                                rule_counts = violations['rule_type'].value_counts()
                                fig1 = px.bar(x=rule_counts.index, y=rule_counts.values, 
                                            title="Violations by Compliance Framework")
                                fig1.update_xaxis(title="Rule Type")
                                fig1.update_yaxis(title="Number of Violations")
                                st.plotly_chart(fig1, use_container_width=True)
                                
                                # Confidence score distribution
                                st.subheader("📊 Confidence Score Distribution")
                                fig2 = px.histogram(violations, x='confidence_score', nbins=10,
                                                  title="Distribution of Violation Confidence Scores")
                                fig2.update_xaxis(title="Confidence Score")
                                fig2.update_yaxis(title="Count")
                                st.plotly_chart(fig2, use_container_width=True)
                                
                                # Timeline of violations (if we have timestamps)
                                if 'created_at' in violations.columns:
                                    st.subheader("⏰ Violations Timeline")
                                    violations['created_at'] = pd.to_datetime(violations['created_at'])
                                    timeline_data = violations.groupby(violations['created_at'].dt.date).size()
                                    fig3 = px.line(x=timeline_data.index, y=timeline_data.values,
                                                  title="Violations Detected Over Time")
                                    fig3.update_xaxis(title="Date")
                                    fig3.update_yaxis(title="Number of Violations")
                                    st.plotly_chart(fig3, use_container_width=True)
                            
                            # Detailed table
                            st.subheader("📋 Detailed Results Table")
                            
                            # Table filters
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                show_violations_only = st.checkbox("Show Violations Only", value=True)
                            with col2:
                                rule_type_filter = st.selectbox("Rule Type", ["All"] + list(results_df['rule_type'].unique()))
                            with col3:
                                min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.0)
                            
                            # Apply filters
                            filtered_results = results_df.copy()
                            if show_violations_only:
                                filtered_results = filtered_results[filtered_results['is_violation'] == True]
                            if rule_type_filter != "All":
                                filtered_results = filtered_results[filtered_results['rule_type'] == rule_type_filter]
                            filtered_results = filtered_results[filtered_results['confidence_score'] >= min_confidence]
                            
                            # Display table
                            if len(filtered_results) > 0:
                                display_cols = ['rule_type', 'violation_type', 'confidence_score', 'explanation']
                                st.dataframe(
                                    filtered_results[display_cols].round(3),
                                    use_container_width=True
                                )
                                
                                # Export functionality
                                if st.button("📥 Export Results to CSV"):
                                    csv = filtered_results.to_csv(index=False)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv,
                                        file_name=f"compliance_results_{doc_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                                        mime="text/csv"
                                    )
                            else:
                                st.info("No results match the current filters.")
                        else:
                            st.info("No compliance analysis results found for this document.")
                    else:
                        st.error("Failed to fetch compliance results.")
            else:
                st.info("No documents available. Please upload documents first.")
                
    except requests.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")

def rule_management_page():
    """Display and manage compliance rules"""
    st.header("⚙️ Rule Management")
    
    try:
        # Get available rules from API
        response = requests.get(f"{API_BASE_URL}/rules/")
        if response.status_code == 200:
            rules_data = response.json()
            rules = rules_data.get("rules", {})
            
            # Rule overview
            st.subheader("📋 Available Compliance Rules")
            
            # Statistics
            total_rules = sum(len(rule_set.get("rules", [])) for rule_set in rules.values())
            rule_types = list(rules.keys())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rules", total_rules)
            with col2:
                st.metric("Rule Types", len(rule_types))
            with col3:
                st.metric("Frameworks", len(rule_types))
            
            # Rule type selector
            selected_rule_type = st.selectbox("Select Rule Type", rule_types)
            
            if selected_rule_type and selected_rule_type in rules:
                rule_set = rules[selected_rule_type]
                st.subheader(f"{selected_rule_type} Rules")
                
                # Rule set info
                if "description" in rule_set:
                    st.info(rule_set["description"])
                
                # Display individual rules
                individual_rules = rule_set.get("rules", [])
                
                for i, rule in enumerate(individual_rules):
                    with st.expander(f"📜 {rule.get('name', f'Rule {i+1}')} - {rule.get('severity', 'MEDIUM')} Severity"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**ID:** {rule.get('id', 'N/A')}")
                            st.write(f"**Description:** {rule.get('description', 'No description available')}")
                            
                            if rule.get("patterns"):
                                st.write("**Patterns:**")
                                for pattern in rule["patterns"]:
                                    st.code(pattern)
                            
                            if rule.get("llm_prompt"):
                                st.write("**LLM Analysis Prompt:**")
                                st.write(rule["llm_prompt"])
                        
                        with col2:
                            st.write(f"**Severity:** {rule.get('severity', 'MEDIUM')}")
                            st.write(f"**Type:** {rule.get('type', 'N/A')}")
                            
                            # Rule actions (placeholder for future functionality)
                            if st.button(f"✏️ Edit", key=f"edit_{rule.get('id', i)}"):
                                st.info("Rule editing functionality coming soon!")
                            
                            if st.button(f"🧪 Test", key=f"test_{rule.get('id', i)}"):
                                st.info("Rule testing functionality coming soon!")
                
                # Rule statistics for this type
                st.subheader(f"📊 {selected_rule_type} Statistics")
                
                if individual_rules:
                    # Severity distribution
                    severity_counts = {}
                    for rule in individual_rules:
                        severity = rule.get('severity', 'MEDIUM')
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    if severity_counts:
                        fig = px.pie(values=list(severity_counts.values()), 
                                   names=list(severity_counts.keys()),
                                   title=f"{selected_rule_type} Rules by Severity")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Rule types (if available)
                    rule_type_counts = {}
                    for rule in individual_rules:
                        rule_type = rule.get('type', 'General')
                        rule_type_counts[rule_type] = rule_type_counts.get(rule_type, 0) + 1
                    
                    if len(rule_type_counts) > 1:
                        fig2 = px.bar(x=list(rule_type_counts.keys()), 
                                     y=list(rule_type_counts.values()),
                                     title=f"{selected_rule_type} Rules by Category")
                        st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error("Failed to fetch rules from API")
            
    except requests.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
    
    # Add new rule section (placeholder)
    st.subheader("➕ Add New Rule")
    with st.expander("Create Custom Rule"):
        st.info("Custom rule creation functionality will be implemented in future versions.")
        
        rule_name = st.text_input("Rule Name")
        rule_description = st.text_area("Rule Description")
        rule_severity = st.selectbox("Severity", ["LOW", "MEDIUM", "HIGH"])
        rule_patterns = st.text_area("Search Patterns (one per line)")
        
        if st.button("💾 Save Rule"):
            st.warning("Rule saving functionality coming soon!")

def check_api_connectivity():
    """Check if the API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def display_api_status():
    """Display API connectivity status in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔌 API Status")
        
        if check_api_connectivity():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.warning("Make sure the FastAPI server is running on localhost:8000")

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

if __name__ == "__main__":
    main()