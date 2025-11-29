public class Test4 {
    static void hello() {
        System.out.println("Hello World");
    }
    static int add(int x, int y) {
        return x + y;
    }
    public static void main(String[] args) {
        hello();
        int result = add(3, 4);
        System.out.println("Add result: " + result);
    }
}
