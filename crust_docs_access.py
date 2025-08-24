#!/usr/bin/env python3
"""
Script to access Crust documentation with authentication
"""

import requests
import getpass
import sys
import os
from urllib.parse import urljoin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CrustDocsClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv('CRUST_DOCS_URL', 'https://fulldocs.crustdata.com')
        self.session = requests.Session()
        self.authenticated = False
    
    def login(self, username=None, password=None):
        """Login to Crust documentation"""
        if not username:
            username = os.getenv('CRUST_EMAIL')
            if not username:
                username = input("Username: ")
        if not password:
            password = os.getenv('CRUST_PASSWORD')
            if not password:
                password = getpass.getpass("Password: ")
        
        # Common login endpoints to try
        login_endpoints = [
            "/api/auth/login",
            "/auth/login",
            "/login",
            "/api/login"
        ]
        
        for endpoint in login_endpoints:
            try:
                login_url = urljoin(self.base_url, endpoint)
                response = self.session.post(login_url, json={
                    "username": username,
                    "password": password
                })
                
                if response.status_code == 200:
                    print(f"✅ Successfully authenticated at {endpoint}")
                    self.authenticated = True
                    return True
                    
            except requests.exceptions.RequestException as e:
                continue
        
        # Try basic auth if API endpoints don't work
        try:
            self.session.auth = (username, password)
            response = self.session.get(self.base_url)
            if response.status_code != 401:
                print("✅ Successfully authenticated using basic auth")
                self.authenticated = True
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("❌ Authentication failed")
        return False
    
    def get_documentation(self, path=""):
        """Fetch documentation from specified path"""
        if not self.authenticated:
            print("Please authenticate first using login()")
            return None
        
        try:
            url = urljoin(self.base_url, path)
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching documentation: {e}")
            return None
    
    def list_available_docs(self):
        """List available documentation sections"""
        common_paths = [
            "/docs/intro",
            "/docs/api",
            "/docs/getting-started", 
            "/docs/developer-guide",
            "/docs/api-reference",
            "/docs/tutorials",
            "/docs/examples"
        ]
        
        print("Checking available documentation sections...")
        available = []
        
        for path in common_paths:
            try:
                response = self.session.get(urljoin(self.base_url, path))
                if response.status_code == 200:
                    available.append(path)
                    print(f"✅ {path}")
                else:
                    print(f"❌ {path} (Status: {response.status_code})")
            except requests.exceptions.RequestException:
                print(f"❌ {path} (Connection error)")
        
        return available

def main():
    client = CrustDocsClient()
    
    if len(sys.argv) > 2:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = None
        password = None
    
    # Authenticate
    if client.login(username, password):
        print("\n" + "="*50)
        print("Crust Documentation Access")
        print("="*50)
        
        while True:
            print("\nOptions:")
            print("1. List available documentation")
            print("2. Get specific documentation path")
            print("3. Download documentation to file")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                client.list_available_docs()
            
            elif choice == "2":
                path = input("Enter documentation path (e.g., /api): ")
                content = client.get_documentation(path)
                if content:
                    print(f"\n--- Documentation from {path} ---")
                    print(content[:2000])  # Show first 2000 chars
                    if len(content) > 2000:
                        print(f"\n... (truncated, total length: {len(content)} chars)")
            
            elif choice == "3":
                path = input("Enter documentation path: ")
                filename = input("Enter filename to save to: ")
                content = client.get_documentation(path)
                if content:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Documentation saved to {filename}")
            
            elif choice == "4":
                print("Goodbye!")
                break
            
            else:
                print("Invalid option")
    
    else:
        print("Failed to authenticate. Please check your credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()