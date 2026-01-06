#include <gtk/gtk.h>
// "" means local directory file.
#include "constants.h"

// Latest open file.
char *current_file;

void destroy (GtkWidget* widget, gpointer data) {
    /**
     * @brief Kill the application.
     * @param
     * @return void
     */
    g_application_quit(G_APPLICATION(data));
}

static void open_file(GtkWidget *btn, gpointer parent_window) {
    GtkWidget *dialog = gtk_file_chooser_dialog_new("Open file", GTK_WINDOW(parent_window), GTK_FILE_CHOOSER_ACTION_OPEN, "Cancel", 0, "OK", 1, NULL);
    if (gtk_dialog_run(GTK_DIALOG(dialog)) == 1) {
        current_file = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
        printf("%s\n", current_file);
    }
    gtk_widget_destroy(dialog);
}

static void activate (GtkApplication *app, gpointer user_data) {
    // Main window.
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), APP_NAME);
    gtk_window_set_default_size(GTK_WINDOW(window), SIZE_W, SIZE_H);

    // Single main container. Window can only have one widget, rest has to be inside.
    GtkWidget *main_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);

    // Menu bar. Is a separate vertical box,
    GtkWidget *menu_bar = gtk_menu_bar_new ();
    GtkWidget *menu_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_box_pack_start(GTK_BOX(menu_box), menu_bar, TRUE, TRUE, 0);

    // Main menu bar button.
    GtkWidget *file_menu_item = gtk_menu_item_new_with_label(STR_FILE);
    gtk_menu_shell_append(GTK_MENU_SHELL(menu_bar), file_menu_item);

    GtkWidget *f_menu = gtk_menu_new();
    gtk_menu_item_set_submenu(GTK_MENU_ITEM(file_menu_item), f_menu);

    GtkWidget *open_menu_item = gtk_menu_item_new_with_label(STR_OPEN);
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), open_menu_item);
    g_signal_connect(open_menu_item, "activate", G_CALLBACK(open_file), window);

    GtkWidget *save_menu_item = gtk_menu_item_new_with_label(STR_SAVE);
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), save_menu_item);

    GtkWidget *quit_menu_item = gtk_menu_item_new_with_label(STR_QUIT);
    gtk_menu_shell_append (GTK_MENU_SHELL(f_menu), quit_menu_item);
    g_signal_connect(quit_menu_item, "activate", G_CALLBACK(destroy), app);

    // Text field.
    GtkWidget *main_text_field = gtk_text_view_new();

    // Status bar.
    GtkWidget *statusbar = gtk_statusbar_new();

    // Every message needs to generate a unique ID.
    const guint id = gtk_statusbar_get_context_id(GTK_STATUSBAR(statusbar), "info");
    gtk_statusbar_push(GTK_STATUSBAR(statusbar), id, STR_STATUS_INIT);
    // Use pop to delete message from the stack.

    // Assembling all components into main box.
    // Add menu box to the main box.
    gtk_box_pack_start(GTK_BOX(main_box), menu_box, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(main_box), main_text_field, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(main_box), statusbar, FALSE, FALSE, 0);

    gtk_container_add(GTK_CONTAINER(window), main_box);

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