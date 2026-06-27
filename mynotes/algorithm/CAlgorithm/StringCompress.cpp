#include <stdio.h>
#include <string.h>
// Ïß -> Ë³Ðò´®¡¢Á´´® ASCII('\0'¡¢48('0')¡¢65('A')¡¢97('a'))
int BF(char s[], char t[])
{
    int i = 0; 
    int j = 0; 
    int lenS = strlen(s);
    int lenT = strlen(t);

    while (i < lenS && j < lenT)
    {
        if (s[i] == t[j])
        {
            i++;
            j++;
        }
        else
        {
            i = i - j + 1;
            j = 0;
        }
    }
    if (j == lenT)
        return i - j;
    else
        return -1;
}
