#include <gtk/gtk.h>
#include <constants.h>

static void activate (GtkApplication *app, gpointer user_data) {
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW (window), APP_NAME);
    gtk_window_set_default_size(GTK_WINDOW (window), SIZE_W, SIZE_H);
    gtk_window_present(GTK_WINDOW (window));
}

int main (int argc, char **argv) {
    int status = 0;

    GtkApplication *app = gtk_application_new(APP_INTERNAL_NAME, G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK (activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}