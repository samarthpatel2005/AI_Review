// JavaScript Test File with Multiple Issues
const apiKey = "sk-test123456789";  // SECURITY: Hardcoded API key
let secretToken = "bearer_abc123";   // SECURITY: Hardcoded token

class UnsafeJSClass {
    constructor() {
        this.data = null;
        // hello test comment  // QUALITY: Test comment
    }
    
    processUserInput(userInput) {
        // SECURITY: XSS vulnerability
        document.getElementById("output").innerHTML = userInput;
        
        console.log("Processing input:", userInput);  // QUALITY: Console.log in production
        
        // SECURITY: SQL injection via template literal
        const query = `SELECT * FROM users WHERE name = '${userInput}'`;
        
        // QUALITY: Loose equality
        if (userInput == null) {  // Should use ===
            return false;
        }
        
        return query;
    }
    
    authenticateUser(username, password) {
        // SECURITY: Eval usage - code injection risk
        const result = eval(`checkUser('${username}', '${password}')`);
        
        // debug comment  // QUALITY: Debug comment
        console.log("Auth result:", result);  // Debug console.log
        
        return result;
    }
    
    divideNumbers(a, b) {
        // QUALITY: No zero check
        return a / b;
    }
    
    // TODO: implement proper validation  // QUALITY: TODO comment
    unsafeAjax(url, data) {
        // SECURITY: No input validation
        fetch(url, {
            method: 'POST',
            body: JSON.stringify(data)
        }).then(response => {
            // Missing error handling
            return response.json();
        });
    }
}

// Global variable usage - QUALITY issue
var globalSecret = "admin_password123";  // SECURITY + QUALITY: var usage + hardcoded secret

function processPayment(amount, cardNumber) {
    // test function  // QUALITY: Test comment
    console.log("Processing payment for:", amount);  // Debug output
    
    // SECURITY: Potential XSS if amount comes from user input
    document.write(`<p>Processing $${amount}</p>`);
    
    // QUALITY: No input validation
    const result = amount / 100;  // Could be division by zero
    
    return result;
}

// SECURITY: Hardcoded credentials
const dbConfig = {
    host: "localhost",
    user: "admin",
    password: "secret123",  // Hardcoded password
    database: "production"
};

// Event handler with potential issues
document.addEventListener('click', function(event) {
    // SECURITY: innerHTML usage without sanitization
    event.target.innerHTML = event.target.getAttribute('data-content');
    
    console.log("Click event processed");  // Debug console.log
});

// hello test - main execution  // Test comment
console.log("App initialized with secret:", globalSecret);  // Exposing secret