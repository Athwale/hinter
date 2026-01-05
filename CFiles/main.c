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
    GtkWidget *field;

    // Main window.
    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), APP_NAME);
    gtk_window_set_default_size(GTK_WINDOW(window), SIZE_W, SIZE_H);

    // Single main container. Window can only have one widget, rest has to be inside.
    box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);

    // Label.
    //label = gtk_label_new("Label");

    // Button.
    //button = gtk_button_new_with_label("Hello World");
    // target, event, function, data.
    //g_signal_connect(button, "clicked", G_CALLBACK(b_click), label);

    // Text input.
    //text = gtk_entry_new();

    // Text field.
    field = gtk_text_view_new();

    // Menu bar. Is a separate vertical box,
    GtkWidget *mbar = gtk_menu_bar_new ();
    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_box_pack_start(GTK_BOX(vbox), mbar, TRUE, TRUE, 0);

    GtkWidget *file_mi = gtk_menu_item_new_with_label("File");
    gtk_menu_shell_append(GTK_MENU_SHELL(mbar), file_mi);

    GtkWidget *f_menu = gtk_menu_new();
    gtk_menu_item_set_submenu (GTK_MENU_ITEM(file_mi), f_menu);
    GtkWidget *quit_mi = gtk_menu_item_new_with_label("Quit");
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), quit_mi);

    g_signal_connect (quit_mi, "activate", G_CALLBACK(end_program),
    NULL);

    // Add menu box to the main box.
    gtk_box_pack_start(GTK_BOX(box), vbox, FALSE, FALSE, 0);

    // Expand, fill
    gtk_box_pack_start(GTK_BOX(box), field, TRUE, TRUE, 0);
    //gtk_box_pack_start(GTK_BOX(box), text, TRUE, TRUE, 0);
    //gtk_box_pack_start(GTK_BOX(box), label, TRUE, TRUE, 0);
    //gtk_box_pack_start(GTK_BOX(box), button, FALSE, FALSE, 0);

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