#include <stdio.h>
int main(){
float terms;
float a;
float b;
float next;
terms = 10;
a = 0;
b = 1;
printf("Fibonacci Sequence:\n");
printf("%.2f\n", (float)(a));
printf("%.2f\n", (float)(b));
for(int i=2;i<terms;i=i+1){
next = a+b;
printf("%.2f\n", (float)(next));
a = b;
b = next;
}
return 0;
}
