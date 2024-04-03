#include <stdio.h>
int main(){
float nums;
printf("How many fibonacci numbers do you want?\n");
if(0==scanf("%f", &nums)) {
nums = 0;
scanf("%*s");
}
return 0;
}
