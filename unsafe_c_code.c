#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char global_password[20] = "admin123"; // Hardcoded secret (bad practice)

// Function to read user input (unsafe)
void getUserInput(char *buffer) {
    printf("Enter your name: ");
    gets(buffer); // Insecure: buffer overflow risk
}

// Function with memory leak and unsafe string handling
char* buildGreeting(char *name) {
    char *greet = malloc(50); // Allocated but never freed
    strcpy(greet, "Hello ");  // Unsafe strcpy
    strcat(greet, name);      // Unsafe strcat
    return greet;
}

// Function simulating SQL query construction (SQL injection risk)
void queryDatabase(char *userInput) {
    char query[200];
    sprintf(query, "SELECT * FROM users WHERE name = '%s';", userInput); // Injection risk
    printf("Executing query: %s\n", query);
}

// Function with division by zero possibility
int divide(int a, int b) {
    return a / b; // No check for b == 0
}

int main() {
    char name[10]; // Too small buffer
    int x, y, result;

    // Using uninitialized variables
    printf("Uninitialized result = %d\n", result);

    getUserInput(name);
    char *greeting = buildGreeting(name);
    printf("%s\n", greeting);

    queryDatabase(name);

    printf("Enter two numbers: ");
    scanf("%d %d", &x, &y);
    printf("Division result: %d\n", divide(x, y));

    // Forgot to free(greeting); --> memory leak

    return 0;
}