#include <gtk/gtk.h>
#include <string.h>
#include <stdio.h>
#include <libgen.h>
// "" means local directory file.
#include "constants.h"

void post_status_message(const char *msg);

// todo https://codebrowser.dev/gtk/gtk/demos/gtk-demo/textview.c.html
// todo valgrind check leaks?
// todo check documentation for transfer and those have to be unrefed.

// Latest open file.
char *current_file;
GtkWidget *status_message;
GtkWidget *main_text_field;
GtkWidget *window;

static void destroy(GSimpleAction *action, GVariant *parameter, gpointer user_data) {
    g_application_quit(G_APPLICATION(user_data));
}

void post_status_message(const char *msg) {
    /**
     * @brief Display a status message at the bottom of the window.
     * @param string message.
     * @return void
     */
    // Every message needs to generate a unique ID.
    gtk_label_set_text(GTK_LABEL(status_message), msg);
}

void update_status() {
    char message[300] = {0};
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));
    int chars = gtk_text_buffer_get_char_count(buffer);
    int lines = gtk_text_buffer_get_line_count(buffer);
    // todo count unique colors
    int colors = 0;

    sprintf(message, "File - %s: Lines: %d, chars: %d, colors: %d", basename(current_file), lines, chars, colors);
    post_status_message(message);
}

void show_dialog(GtkWidget *parent, const gchar *title, const gchar *message) {
    GtkAlertDialog *dialog = gtk_alert_dialog_new(title);
    const char *buttons[] = {STR_OK, nullptr};
    gtk_alert_dialog_set_detail(dialog, message);
    gtk_alert_dialog_set_buttons(dialog, buttons);
    gtk_alert_dialog_set_cancel_button(dialog, 0);
    gtk_alert_dialog_set_default_button(dialog, 0);
    gtk_alert_dialog_choose(dialog, GTK_WINDOW(parent), nullptr, nullptr, NULL);
}

static void create_tags(GtkTextBuffer *buffer) {
    // todo tag table could be separate and reused in new buffers on new file load.
    gtk_text_buffer_create_tag(buffer, "italic", "style", PANGO_STYLE_ITALIC, NULL);
    gtk_text_buffer_create_tag(buffer, "bold", "weight", PANGO_WEIGHT_BOLD, NULL);
    gtk_text_buffer_create_tag(buffer, "red_background", "background", "red", NULL);
}

static void on_file_open(GObject *source_object, GAsyncResult *result, gpointer user_data) {
    GtkFileDialog *dialog = GTK_FILE_DIALOG(source_object);
    GError *error = nullptr;

    GFile *file = gtk_file_dialog_open_finish(dialog, result, &error);
    if (file != NULL) {
        current_file = g_file_get_path(file);
        GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));

        // Open text file in read only mode
        FILE *text_file  = fopen(current_file, "r");
        char line[1024];
        GtkTextIter iter;

        if (text_file == NULL) {
            // If file can not be opened, show error and exit.
            show_dialog(window, STR_ERR, STR_FILE_OPEN_FAIL);
            return;
        }

        // Get iterator at the start of the buffer. Each insert will move the iterator further.
        gtk_text_buffer_get_iter_at_offset (buffer, &iter, 0);
        while(fgets(line, 1024, text_file)) {
            // Insert until null character.
            gtk_text_buffer_insert(buffer, &iter, line, -1);
        }
        fclose(text_file);
        g_object_unref(file);
    } else {
        // Error or Cancellation
        // If the user cancelled, error->code will be GTK_DIALOG_ERROR_DISMISSED
        show_dialog(window, STR_ERR, STR_FILE_OPEN_FAIL);
        g_error_free(error);
    }
}

static void show_file_chooser_dialog(GtkButton *btn, gpointer user_data) {
    GtkFileDialog *dialog = gtk_file_dialog_new();
    gtk_file_dialog_set_title(dialog, "Open Text File");

    GtkFileFilter *filter = gtk_file_filter_new();
    gtk_file_filter_set_name(filter, "Text Files");
    gtk_file_filter_add_pattern(filter, "*.txt");

    GListStore *filters = g_list_store_new(GTK_TYPE_FILE_FILTER);
    g_list_store_append(filters, filter);
    gtk_file_dialog_set_filters(dialog, G_LIST_MODEL(filters));
    g_object_unref(filters);
    g_object_unref(filter);

    gtk_file_dialog_open(dialog, GTK_WINDOW(window), nullptr, on_file_open, NULL);
    g_object_unref(dialog);
}

static void new_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked New.\n");
}

static void open_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    show_file_chooser_dialog(nullptr, user_data);
}

static void save_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Save.\n");
}

static void undo_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));
    gtk_text_buffer_undo(buffer);
}

static void redo_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));
    gtk_text_buffer_redo(buffer);
}

static void setup_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Setup.\n");
}

static void bold_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    GtkTextIter start;
    GtkTextIter end;
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));
    if (!gtk_text_buffer_get_selection_bounds(buffer, &start, &end)) {
        return;
    }

    GtkTextTagTable *table = gtk_text_buffer_get_tag_table(buffer);
    GtkTextTag *tag = gtk_text_tag_table_lookup(table, "bold");
    if (gtk_text_iter_has_tag(&start, tag)) {
        gtk_text_buffer_remove_tag(buffer, tag, &start, &end);
    } else {
        gtk_text_buffer_apply_tag(buffer, tag, &start, &end);
    }
}

static void italic_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Italic.\n");
}

static void colorize_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Colorize.\n");
}

static void spelling_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Spelling.\n");
}

static void find_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Find.\n");
}

static void startup(GApplication *application) {
    // Called in startup handler because that is called only once.
    GtkApplication *app = GTK_APPLICATION(application);

    GSimpleAction *act_quit = g_simple_action_new("quit", nullptr);
    g_action_map_add_action(G_ACTION_MAP(app), G_ACTION(act_quit));
    g_signal_connect(act_quit, "activate", G_CALLBACK(destroy), NULL);

    GSimpleAction *act_open = g_simple_action_new("open", nullptr);
    g_action_map_add_action(G_ACTION_MAP(app), G_ACTION(act_open));
    g_signal_connect(act_open, "activate", G_CALLBACK(show_file_chooser_dialog), NULL);

    GMenu *menubar = g_menu_new();

    // Button on menu bar.
    GMenuItem *main_menu_file = g_menu_item_new(STR_FILE, nullptr);

    // Menu that goes under File.
    GMenu *file_menu = g_menu_new();
    // Add button into menu.
    // app. is an action map identifier where gtk will look for new...
    GMenuItem *menu_item_new = g_menu_item_new(STR_NEW, "app.new");
    g_menu_append_item(file_menu, menu_item_new);
    GMenuItem *menu_item_open = g_menu_item_new(STR_OPEN, "app.open");
    g_menu_append_item(file_menu, menu_item_open);
    GMenuItem *menu_item_save = g_menu_item_new(STR_SAVE, "app.save");
    g_menu_append_item(file_menu, menu_item_save);
    GMenuItem *menu_item_quit = g_menu_item_new(STR_QUIT, "app.quit");
    g_menu_append_item(file_menu, menu_item_quit);
    // Add file menu under File button.
    g_menu_item_set_submenu(main_menu_file, G_MENU_MODEL(file_menu));
    // Add File button on menubar.
    g_menu_append_item(menubar, main_menu_file);

    // Once inserted, menu item is copied into the menu and should be freed.
    g_object_unref(file_menu);
    g_object_unref(menu_item_quit);
    g_object_unref(menu_item_open);
    g_object_unref(menu_item_save);
    g_object_unref(main_menu_file);

    gtk_application_set_menubar(GTK_APPLICATION(app), G_MENU_MODEL(menubar));
}

static void activate(GtkApplication *app, gpointer user_data) {
    // Main window.
    window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), APP_NAME);
    gtk_window_set_default_size(GTK_WINDOW(window), SIZE_W, SIZE_H);

    // Single main container. Window can only have one widget, rest has to be inside.
    GtkWidget *main_box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    //gtk_box_set_homogeneous(GTK_BOX(main_box), TRUE);

    // Toolbar.
    // Array of pointers. A ragged array of strings because each array of characters is of different length. String is a pointer o the start of the string.
    // https://gitlab.gnome.org/World/design/icon-library/-/tree/master/data/resources/icon-dev-kit
    const char *icon_names[] = {
        "document-new",
        "document-open",
        "document-save",
        "edit-undo",
        "edit-redo",
        "document-properties",
        "format-text-bold",
        "format-text-italic",
        "applications-graphics",
        "tools-check-spelling",
        "edit-find"
    };
    // Create array of function pointers Syntax: return_type (*name[])(args)
    static void (*callbacks[])(GSimpleAction *, GVariant *, gpointer) = {
        new_file_callback,
        open_file_callback,
        save_file_callback,
        undo_file_callback,
        redo_file_callback,
        setup_file_callback,
        bold_file_callback,
        italic_file_callback,
        colorize_file_callback,
        spelling_file_callback,
        find_file_callback
    };
    GtkWidget *toolbar_box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 3);
    // Sizeof work because they are pointers of equal size.
    for (int i = 0; i < sizeof(icon_names) / sizeof(icon_names[0]); i++) {
        GtkWidget *button = gtk_button_new_from_icon_name(icon_names[i]);
        // user_data will be window.
        g_signal_connect(button, "clicked", G_CALLBACK(callbacks[i]), NULL);
        gtk_box_append(GTK_BOX(toolbar_box), button);
    }

    // Status bar.
    GtkWidget *status_bar = gtk_box_new(GTK_ORIENTATION_VERTICAL, 3);
    status_message = gtk_label_new(STR_STATUS_INIT);
    gtk_box_append(GTK_BOX(status_bar), status_message);

    // Main text field is declared outside of function to be accessible everywhere.
    GtkTextBuffer *buffer = gtk_text_buffer_new(nullptr);
    main_text_field = gtk_text_view_new_with_buffer(buffer);
    create_tags(buffer);
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(main_text_field), GTK_WRAP_WORD);

    GtkWidget *scrolled_window = gtk_scrolled_window_new();
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window), GTK_POLICY_AUTOMATIC,
                                   GTK_POLICY_AUTOMATIC);

    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scrolled_window), main_text_field);

    // Assembling all components into main box.
    gtk_widget_set_hexpand(toolbar_box, TRUE);
    gtk_widget_set_hexpand(status_bar, TRUE);
    gtk_widget_set_halign(status_message, GTK_ALIGN_START);
    gtk_widget_set_halign(toolbar_box, GTK_ALIGN_FILL);
    gtk_widget_set_valign(toolbar_box, GTK_ALIGN_FILL);

    gtk_widget_set_hexpand(main_text_field, TRUE);
    gtk_widget_set_vexpand(main_text_field, TRUE);
    gtk_widget_set_halign(main_text_field, GTK_ALIGN_FILL);
    gtk_widget_set_valign(main_text_field, GTK_ALIGN_FILL);

    gtk_box_append(GTK_BOX(main_box), toolbar_box);
    gtk_box_append(GTK_BOX(main_box), scrolled_window);
    gtk_box_append(GTK_BOX(main_box), status_bar);

    gtk_window_set_child(GTK_WINDOW(window), main_box);

    gtk_application_window_set_show_menubar(GTK_APPLICATION_WINDOW(window), TRUE);
    // GTK4 by default shows all widgets, but the top level one needs to be presented manually. Present moves it up to
    // the front of all windows.
    gtk_window_present(GTK_WINDOW(window));

    update_status();
}

int main(int argc, char **argv) {
    int status = 0;

    GtkApplication *app = gtk_application_new(APP_INTERNAL_NAME, G_APPLICATION_DEFAULT_FLAGS);
    // Call activate handler when the application starts.
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    g_signal_connect (app, "startup", G_CALLBACK(startup), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}
