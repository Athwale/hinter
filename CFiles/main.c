#include <gtk/gtk.h>
// "" means local directory file.
#include "constants.h"

void end_program(GtkWidget *w, gpointer ptr) {
    gtk_main_quit();
}

void b_click(GtkWidget *wid, gpointer ptr) {
    // wid is the widget that generated the signal.
    // ptr is an optional target passed into the function.
    gtk_label_set_text (GTK_LABEL(ptr), "Pressed");
}

static void activate (GtkApplication *app, gpointer user_data) {
    GtkWidget *window;
    GtkWidget *button;
    GtkWidget *box;
    GtkWidget *label;
    GtkWidget *text;

    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), APP_NAME);
    gtk_window_set_default_size(GTK_WINDOW(window), 200, 200);

    // Container.
    box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 20);

    // Label.
    label = gtk_label_new("Label");

    // Button.
    button = gtk_button_new_with_label("Hello World");
    // target, event, function, data.
    g_signal_connect(button, "clicked", G_CALLBACK(b_click), label);

    // Text input.
    text = gtk_entry_new();

    // Expand, fill
    gtk_box_pack_start(GTK_BOX(box), text, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(box), label, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(box), button, FALSE, FALSE, 0);

    gtk_container_add(GTK_CONTAINER(window), box);

    gtk_widget_show_all(window);
}

int main (int argc, char **argv) {
    int status = 0;

    GtkApplication *app = gtk_application_new(APP_INTERNAL_NAME, G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK (activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}