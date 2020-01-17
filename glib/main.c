#include <glib.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    GString *s = g_string_new("hello world");
    printf("Hello there.\n");
    g_string_free(s, TRUE);
    return 0;
}
