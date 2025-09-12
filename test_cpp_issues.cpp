// C++ Test File with Multiple Issues
#include <iostream>
#include <cstring>
#include <cstdlib>

using namespace std;

string api_secret = "sk-abc123456789";  // Hardcoded secret - SECURITY ISSUE

class UnsafeClass {
private:
    char* buffer;
    
public:
    UnsafeClass() {
        buffer = (char*)malloc(100);  // Memory allocation without proper cleanup
    }
    
    void unsafeInput() {
        char input[50];
        cout << "Enter data: ";
        gets(input);  // SECURITY: Buffer overflow vulnerability
        strcpy(buffer, input);  // SECURITY: Unsafe string copy
    }
    
    void processData(const char* data) {
        char query[200];
        sprintf(query, "SELECT * FROM users WHERE name = '%s'", data);  // SECURITY: SQL injection + buffer overflow
        cout << query << endl;  // Debug output
    }
    
    int divide(int a, int b) {
        return a / b;  // QUALITY: Division by zero risk
    }
    
    // hello test - this is a test comment  // QUALITY: Test comment
    void debugFunction() {
        cout << "Debug mode active" << endl;  // Debug statement
        // TODO: fix this later  // QUALITY: TODO comment
        system("ls -la");  // SECURITY: Command execution
    }
};

int main() {
    UnsafeClass obj;
    
    // test comment here  // Test comment
    obj.unsafeInput();
    obj.processData("admin'; DROP TABLE users; --");
    
    cout << "API Secret: " << api_secret << endl;  // SECURITY: Exposing secret
    
    int result = obj.divide(10, 0);  // Division by zero
    cout << "Result: " << result << endl;
    
    return 0;
    // Missing: delete[] buffer; - QUALITY: Memory leak
}