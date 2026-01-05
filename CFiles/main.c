#include <gtk/gtk.h>
// "" means local directory file.
#include "constants.h"

void b_click(GtkWidget *wid, gpointer ptr) {
    // wid is the widget that generated the signal.
    // ptr is an optional target passed into the function.
    gtk_label_set_text (GTK_LABEL(ptr), "Pressed");
}

void destroy (GtkWidget* widget, gpointer data) {
    g_application_quit(G_APPLICATION(data));
}

static void open_file(GtkWidget *btn, gpointer ptr) {
    GtkWidget *dialog = gtk_file_chooser_dialog_new("Open file", GTK_WINDOW(ptr), GTK_FILE_CHOOSER_ACTION_OPEN, "Cancel", 0, "OK", 1, NULL);
    if (gtk_dialog_run(GTK_DIALOG(dialog)) == 1) {
        printf("%s selected\n", gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog)));
    }
    gtk_widget_destroy(dialog);
}

static void activate (GtkApplication *app, gpointer user_data) {
    GtkWidget *window;
    GtkWidget *box;
    GtkWidget *button;
    GtkWidget *label;
    GtkWidget *text;
    GtkWidget *main_text_field;
    // todo add https://stackoverflow.com/questions/1953255/how-does-gtk-statusbar-work-whats-wrong-with-my-code
    // todo what are static functions for?
    GtkWidget *statusbar;

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

    // Menu bar. Is a separate vertical box,
    GtkWidget *menu_bar = gtk_menu_bar_new ();
    GtkWidget *menu_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_box_pack_start(GTK_BOX(menu_box), menu_bar, TRUE, TRUE, 0);

    GtkWidget *file_mi = gtk_menu_item_new_with_label("File");
    gtk_menu_shell_append(GTK_MENU_SHELL(menu_bar), file_mi);

    GtkWidget *f_menu = gtk_menu_new();
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(file_mi), f_menu);

    GtkWidget *open_mi = gtk_menu_item_new_with_label("Open...");
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), open_mi);
    g_signal_connect(open_mi, "activate", G_CALLBACK(open_file), window);

    GtkWidget *save_mi = gtk_menu_item_new_with_label("Save...");
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), save_mi);

    GtkWidget *quit_mi = gtk_menu_item_new_with_label("Quit");
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), quit_mi);
    g_signal_connect(quit_mi, "activate", G_CALLBACK(destroy), app);

    // Text field.
    main_text_field = gtk_text_view_new();

    // Status bar.
    statusbar = gtk_statusbar_new();

    // Every message needs to generate a unique ID.
    guint id = gtk_statusbar_get_context_id(GTK_STATUSBAR(statusbar), "info");
    gtk_statusbar_push(GTK_STATUSBAR(statusbar), id, "Initialized");
    // Use pop to delete message from the stack.

    // Assembling all components into main box.
    // Add menu box to the main box.
    gtk_box_pack_start(GTK_BOX(box), menu_box, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(box), main_text_field, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(box), statusbar, FALSE, FALSE, 0);

    gtk_container_add(GTK_CONTAINER(window), box);

    gtk_widget_show_all(window);
}

int main (int argc, char **argv) {
    int status = 0;

    GtkApplication *app = gtk_application_new(APP_INTERNAL_NAME, G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}