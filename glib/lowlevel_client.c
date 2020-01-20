/*
 * Copyright 2020 Nathan Miller <nathanm2@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <gio/gio.h>
#include <glib.h>
#include <glib/gstdio.h>
#include <stdbool.h>

/* Error Reporting: */

static void print_errorv(const char *fmt, va_list args)
{
    g_fprintf(stderr, "%s: ", g_get_prgname());
    g_vfprintf(stderr, fmt, args);
    g_fprintf(stderr, "\n");
}

static void print_error(const char *fmt, ...)
{
    va_list args;

    va_start(args, fmt);
    print_errorv(fmt, args);
    va_end(args);
}

static void print_gerror(GError *gerror)
{
    if (!gerror)
        return;

    g_fprintf(stderr, "%s: %s [%d]\n", g_quark_to_string(gerror->domain),
              gerror->message, gerror->code);
}

/* Common Options: */

static const char *common_parameters = "<command> <command-opts>";
static const char *common_summary =
    "Glib-based DBus client for test service.\n"
    "\n"
    "Supported Commands:\n"
    "  echo         Send a string, recieve the same string.\n"
    "  wait         Stall for a specified amount of time.\n"
    "\n"
    "Run 'client <command> --help' for command specific help.";

static GOptionEntry common_options[] = {
    /* Add any common options here: */
    {NULL},
};

static GOptionContext *common_option_context(const char *parameter_string,
                                             const char *summary, bool strict)
{
    GOptionContext *opt_ctx;

    opt_ctx = g_option_context_new(parameter_string);

    g_option_context_set_summary(opt_ctx, summary);
    g_option_context_add_main_entries(opt_ctx, common_options, NULL);
    g_option_context_set_strict_posix(opt_ctx, strict);

    return opt_ctx;
}

static void show_help(GOptionContext *opt_ctx)
{
    char *help_str = g_option_context_get_help(opt_ctx, false, NULL);
    fwrite(help_str, 1, strlen(help_str), stdout);
    g_free(help_str);
}

static bool parse_options(GOptionContext *opt_ctx, int *argc, char ***argv,
                          int *status)
{
    GError *gerror = NULL;
    bool rc = g_option_context_parse(opt_ctx, argc, argv, &gerror);

    g_assert(status);

    if (!rc) {
        print_error("option parsing failed: %s", gerror->message);
        g_error_free(gerror);
        *status = -1;
    }

    return rc;
}

/* Connection Utilities */

/* Echo Command */

static const char *echo_parameters = "echo [STRING]";
static const char *echo_summary = "Send a string to the 'EchoString' method.";

static int do_echo(int argc, char **argv)
{
    GOptionContext *opt_ctx;
    int rc = -1;
    GError *gerror = NULL;
    GDBusConnection *connection = NULL;
    GVariant *reply = NULL;
    char *reply_str = NULL;

    opt_ctx = common_option_context(echo_parameters, echo_summary, false);
    if (!parse_options(opt_ctx, &argc, &argv, &rc))
        goto cleanup;

    if (argc < 2) {
        print_error("string argument required.");
        goto cleanup;
    } else if (argc > 2) {
        print_error("too many arguments.");
        goto cleanup;
    }

    connection = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, &gerror);
    if (!connection) {
        print_gerror(gerror);
        goto cleanup;
    }

    reply = g_dbus_connection_call_sync(
        connection, "com.wdc.TestService1", "/com/wdc/TestService1",
        "com.wdc.TestService1", "EchoString", g_variant_new("(s)", argv[1]),
        G_VARIANT_TYPE("(s)"), G_DBUS_CALL_FLAGS_NONE, -1, NULL, &gerror);
    if (!reply) {
        print_gerror(gerror);
        goto cleanup;
    }

    g_variant_get(reply, "(s)", &reply_str);
    printf("%s\n", reply_str);
    rc = 0;

cleanup:

    g_option_context_free(opt_ctx);
    if (connection)
        g_object_unref(connection);
    if (gerror)
        g_error_free(gerror);
    if (reply)
        g_variant_unref(reply);
    if (reply_str)
        g_free(reply_str);
    return rc;
}

/* Wait Command */

static const char *wait_parameters = "wait [SECONDS]";
static const char *wait_summary = "Block in a method for SECONDS.";

static int do_wait(int argc, char **argv)
{
    GOptionContext *opt_ctx;
    int rc = -1;
    GError *gerror = NULL;
    GDBusConnection *connection = NULL;
    char *endptr = NULL;
    int64_t wait;

    opt_ctx = common_option_context(wait_parameters, wait_summary, false);
    if (!parse_options(opt_ctx, &argc, &argv, &rc))
        goto cleanup;

    if (argc < 2) {
        print_error("SECONDS argument required.");
        goto cleanup;
    } else if (argc > 2) {
        print_error("too many arguments.");
        goto cleanup;
    }

    wait = g_ascii_strtoll(argv[1], &endptr, 0);
    if (*endptr != '\0') {
        print_error("cannot convert %s to integer.", argv[1]);
        goto cleanup;
    }

    connection = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, &gerror);
    if (!connection) {
        print_gerror(gerror);
        goto cleanup;
    }

    g_dbus_connection_call_sync(connection, "com.wdc.TestService1",
                                "/com/wdc/TestService1", "com.wdc.TestService1",
                                "Wait", g_variant_new("(t)", wait), NULL,
                                G_DBUS_CALL_FLAGS_NONE, -1, NULL, &gerror);
    if (gerror) {
        print_gerror(gerror);
        goto cleanup;
    }

    rc = 0;

cleanup:

    g_option_context_free(opt_ctx);
    if (connection)
        g_object_unref(connection);
    if (gerror)
        g_error_free(gerror);
    return rc;
}

int main(int argc, char **argv)
{
    GOptionContext *opt_ctx;
    int rc = 0;

    opt_ctx = common_option_context(common_parameters, common_summary, true);

    if (!parse_options(opt_ctx, &argc, &argv, &rc)) {
        goto cleanup;
    }

    if (argc <= 1) {
        show_help(opt_ctx);
        goto cleanup;
    }

    /* Get the verb in the argv[0] position: */
    argv++;
    argc--;

    if (!g_strcmp0(argv[0], "echo")) {
        rc = do_echo(argc, argv);
    } else if (!g_strcmp0(argv[0], "wait")) {
        rc = do_wait(argc, argv);
    } else {
        print_error("unrecognized command '%s'", argv[0]);
        rc = -1;
        goto cleanup;
    }

cleanup:
    g_option_context_free(opt_ctx);

    return rc;
}
