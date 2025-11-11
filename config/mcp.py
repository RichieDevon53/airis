from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "search-suggestion": {
        "url": "https://uat-genai-soap.siloamhospitals.com/suggestion/mcp",
        "transport": "streamable_http"
    }
})
