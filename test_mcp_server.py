"""
Test script to verify MCP Search Server is working
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables BEFORE importing other modules
from dotenv import load_dotenv
load_dotenv()

from src.tools.mcp_client import SearchMCPClientSync

def test_mcp_search():
    """Test MCP search server"""
    print("Testing MCP Search Server...")
    print("="*60)
    
    try:
        # Test with synchronous client
        with SearchMCPClientSync(verbose=True) as client:
            print("\n✓ MCP server started successfully")
            print("\nPerforming test search...")
            
            results = client.search("test query", num_results=3)
            
            print("\n✓ Search completed")
            print("\nResults:")
            print(results)
            
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED - MCP Server is working!")
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_mcp_search()
