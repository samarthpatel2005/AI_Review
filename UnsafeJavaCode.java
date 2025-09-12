// Java Test File with Multiple Issues
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class UnsafeJavaCode {
    // SECURITY: Hardcoded credentials
    private static final String DB_PASSWORD = "admin123";
    private static final String API_SECRET = "sk-java123456";
    
    private Connection connection;
    
    public UnsafeJavaCode() {
        // hello test constructor  // QUALITY: Test comment
        System.out.println("Initializing with secret: " + API_SECRET);  // SECURITY + QUALITY
    }
    
    // SECURITY: SQL Injection vulnerability
    public List<User> getUsersByName(String userName) throws SQLException {
        Statement stmt = connection.createStatement();
        
        // SECURITY: String concatenation in SQL - injection risk
        String query = "SELECT * FROM users WHERE name = '" + userName + "'";
        System.out.println("Executing query: " + query);  // QUALITY: System.out usage
        
        ResultSet rs = stmt.executeQuery(query);
        List<User> users = new ArrayList<>();
        
        while (rs.next()) {
            users.add(new User(rs.getString("name"), rs.getString("email")));
        }
        
        // QUALITY: Resource leak - ResultSet and Statement not closed
        return users;
    }
    
    // SECURITY: Command injection risk
    public String executeSystemCommand(String userInput) throws IOException {
        // debug comment  // QUALITY: Debug comment
        System.out.println("Executing command: " + userInput);  // Debug output
        
        // SECURITY: Runtime.exec with user input
        Process process = Runtime.getRuntime().exec("ls " + userInput);
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
        }
        
        // QUALITY: Resource not closed properly
        return output.toString();
    }
    
    // QUALITY: Division by zero risk
    public double calculatePercentage(int value, int total) {
        // TODO: add validation  // QUALITY: TODO comment
        return (double) value / total;  // No zero check
    }
    
    // SECURITY: Deserialization vulnerability
    public Object deserializeData(byte[] data) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        
        // SECURITY: Unsafe deserialization
        Object obj = ois.readObject();
        
        System.out.println("Deserialized object: " + obj);  // Debug output
        
        return obj;
    }
    
    // QUALITY: Poor exception handling
    public void connectToDatabase() {
        try {
            String url = "jdbc:mysql://localhost:3306/testdb";
            connection = DriverManager.getConnection(url, "admin", DB_PASSWORD);
            
            // test connection  // QUALITY: Test comment
            System.out.println("Connected to database");  // Debug output
            
        } catch (Exception e) {
            // QUALITY: Catching generic Exception
            e.printStackTrace();  // Poor error handling
        }
    }
    
    // QUALITY: Method too long and does too many things
    public void processUserData(String userData) {
        System.out.println("Processing user data");  // Debug output
        
        // Multiple responsibilities in one method
        String[] parts = userData.split(",");
        
        for (int i = 0; i < parts.length; i++) {
            String part = parts[i];
            
            // QUALITY: Potential array index out of bounds
            System.out.println("Part " + i + ": " + part);
            
            // SECURITY: Potential injection if part contains SQL
            String insertQuery = "INSERT INTO data VALUES ('" + part + "')";
            
            try {
                Statement stmt = connection.createStatement();
                stmt.executeUpdate(insertQuery);
                // Resource leak - statement not closed
                
            } catch (SQLException e) {
                System.out.println("Error: " + e.getMessage());  // Poor error handling
            }
        }
        
        // hello test - end of method  // Test comment
    }
    
    public static void main(String[] args) {
        UnsafeJavaCode app = new UnsafeJavaCode();
        
        // test main method  // Test comment
        System.out.println("Starting application with password: " + DB_PASSWORD);  // SECURITY
        
        app.connectToDatabase();
        
        // QUALITY: Hard-coded test data
        app.processUserData("admin'; DROP TABLE users; --");
        
        // Missing proper cleanup and resource management
    }
}

class User {
    private String name;
    private String email;
    
    public User(String name, String email) {
        this.name = name;
        this.email = email;
        
        // debug constructor  // Test comment
        System.out.println("Created user: " + name);  // Debug output
    }
    
    // QUALITY: Missing getters/setters, equals, hashCode
}