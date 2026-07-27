/**
 * Example Java code with various code smells
 * Used for testing detection rules
 */

public class ExampleJavaCode {

    // JV012: Mutable static field
    static List<String> names;

    // JV012: Proper final static
    static final String CONSTANT = "value";

    // JV001: Unused variable
    private int unusedValue;

    // JV009: Magic number
    private int maxAttempts = 42;

    /**
     * JV002: Long method (exceeds 50 lines)
     */
    public void longMethodWithManyLines() {
        int x = 1;
        int y = 2;
        int z = 3;
        int a = 4;
        int b = 5;
        int c = 6;
        int d = 7;
        int e = 8;
        int f = 9;
        int g = 10;
        int h = 11;
        int i = 12;
        int j = 13;
        int k = 14;
        int l = 15;
        int m = 16;
        int n = 17;
        int o = 18;
        int p = 19;
        int q = 20;
        int r = 21;
        int s = 22;
        int t = 23;
        int u = 24;
        int v = 25;
        int w = 26;
        System.out.println(x + y + z);
    }

    /**
     * JV005: Missing null check
     */
    public void processObject(String obj) {
        System.out.println(obj.length()); // No null check!
    }

    /**
     * JV006: Empty catch block
     */
    public void readFile() {
        try {
            int x = 1 / 0;
        } catch (Exception e) {
            // Empty!
        }
    }

    /**
     * JV008: String concatenation in loop
     */
    public String buildString() {
        String result = "";
        for (int i = 0; i < 100; i++) {
            result += "Item " + i + "\n"; // Performance issue!
        }
        return result;
    }

    /**
     * JV014: Verbose logging
     */
    public void processData(List<String> items) {
        System.out.println("Starting processing");
        for (String item : items) {
            System.out.println("Processing: " + item);
            System.out.println("Item length: " + item.length());
            System.out.println("Item uppercase: " + item.toUpperCase());
            System.out.println("Done with " + item);
        }
        System.out.println("Finished processing");
    }

    /**
     * JV015: Resource leak
     */
    public void readFileUnsafely() {
        try {
            FileInputStream fis = new FileInputStream("file.txt");
            int data = fis.read();
            // Never closed!
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * JV003: Class with many methods (if extended)
     */
    public void method1() {}
    public void method2() {}
    public void method3() {}
    public void method4() {}
    public void method5() {}

    /**
     * JV004: Simple getter (suggest Lombok)
     */
    private String name;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    /**
     * JV013: Duplicate code
     */
    public void validateInput1(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }
        if (input.isEmpty()) {
            throw new IllegalArgumentException("Input cannot be empty");
        }
    }

    public void validateInput2(String input) {
        if (input == null) {
            throw new IllegalArgumentException("Input cannot be null");
        }
        if (input.isEmpty()) {
            throw new IllegalArgumentException("Input cannot be empty");
        }
    }
}

// JV011: Class naming convention violation
class anotherClass {
    public void someMethod() {
        // Lowercase class name
    }
}
