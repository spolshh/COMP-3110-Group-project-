public class Test3 {
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            System.out.println("Number: " + i);
        }
        int total = 0;
        for (int j = 1; j <= 5; j++) {
            total += j;
        }
        System.out.println("Total: " + total);
    }
}
