#include <gtk/gtk.h>
#include <string.h>
#include <stdio.h>
#include <libgen.h>
// "" means local directory file.
#include "constants.h"

void post_status_message(const char *msg);

// todo https://codebrowser.dev/gtk/gtk/demos/gtk-demo/textview.c.html
// todo walgrind check leaks?
// todo check documentation for transfer and those have to be unrefed.

// Latest open file.
char *current_file;
GtkWidget *main_text_field;
GtkWidget *statusbar;

void destroy(GtkWidget* widget, gpointer data) {
    /**
     * @brief Kill the application.
     * @param
     * @return void
     */
    g_application_quit(G_APPLICATION(data));
}

void show_dialog(GtkWindow *parent, const gchar *title, const gchar *message) {
    const GtkDialogFlags flags = GTK_DIALOG_DESTROY_WITH_PARENT | GTK_DIALOG_MODAL;

    GtkWidget *dialog = gtk_dialog_new_with_buttons(title, parent, flags, "OK", GTK_RESPONSE_NONE, NULL);
    const int height = 100;
    gtk_window_set_default_size(GTK_WINDOW(dialog), 200, height);

    GtkWidget *content_area = gtk_dialog_get_content_area(GTK_DIALOG(dialog));
    GtkWidget *box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 0);
    GtkWidget *label = gtk_label_new(message);
    gtk_box_pack_start(GTK_BOX(box), label, TRUE, FALSE, height/2);

    gtk_container_add(GTK_CONTAINER(content_area), box);

    g_signal_connect_swapped(dialog, "response", G_CALLBACK(gtk_widget_destroy), dialog);
    gtk_widget_show_all(dialog);
}

void update_status() {
    char message[300] = {0};
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));
    int chars = gtk_text_buffer_get_char_count(buffer);
    int lines = gtk_text_buffer_get_line_count(buffer);

    sprintf(message, "File - %s: Lines: %d, chars: %d, colors: ", basename(current_file), lines, chars);
    post_status_message(message);
}

void post_status_message(const char *msg) {
    /**
     * @brief Display a status message at the bottom of the window.
     * @param string message.
     * @return void
     */
    // Every message needs to generate a unique ID.
    const guint id = gtk_statusbar_get_context_id(GTK_STATUSBAR(statusbar), "info");
    gtk_statusbar_remove_all(GTK_STATUSBAR(statusbar), id);
    gtk_statusbar_push(GTK_STATUSBAR(statusbar), id, msg);
}

static void create_tags(GtkTextBuffer *buffer) {
    // todo tag table could be separate and reused in new buffers.
    gtk_text_buffer_create_tag(buffer, "italic", "style", PANGO_STYLE_ITALIC, NULL);
    gtk_text_buffer_create_tag(buffer, "bold", "weight", PANGO_WEIGHT_BOLD, NULL);
    gtk_text_buffer_create_tag(buffer, "red_background", "background", "red", NULL);
}

static void open_file(GtkWidget *btn, gpointer parent_window) {
    GtkWidget *dialog = gtk_file_chooser_dialog_new("Open file", GTK_WINDOW(parent_window), GTK_FILE_CHOOSER_ACTION_OPEN, "Cancel", 0, "OK", 1, NULL);
    if (gtk_dialog_run(GTK_DIALOG(dialog)) == 1) {
        current_file = gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog));
        GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));

        // Open text file in read only mode
        FILE *text_file  = fopen(current_file, "r");
        char line[1024];
        GtkTextIter iter;

        if (text_file == NULL) {
            // If file can not be opened, show error and exit.
            show_dialog(parent_window, STR_ERR, STR_FILE_OPEN_FAIL);
            return;
        }

        // Get iterator at the start of the buffer. Each insert will move the iterator further.
        gtk_text_buffer_get_iter_at_offset (buffer, &iter, 0);
        while(fgets(line, 1024, text_file)) {
            // Insert until null character.
            gtk_text_buffer_insert(buffer, &iter, line, -1);
        }
        fclose(text_file);
    }
    gtk_widget_destroy(dialog);

    // todo load metadata file.

    update_status();
}

static void new_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked New.\n");
}

static void save_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Save.\n");
}

static void undo_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    GtkTextBuffer *buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(main_text_field));
    // todo gtk4???
    //gtk_text_buffer_undo(buffer);
}

static void redo_file_callback(GSimpleAction *simple, GVariant *parameter, gpointer user_data) {
    g_print("You clicked Redo.\n");
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
    // todo undo, redo how?

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

static void activate(GtkApplication *app, gpointer user_data) {
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

    // Toolbar.
    GtkWidget *toolbar = gtk_toolbar_new();
    gtk_toolbar_set_style(GTK_TOOLBAR(toolbar), GTK_TOOLBAR_ICONS);
    gtk_toolbar_set_icon_size(GTK_TOOLBAR(toolbar), GTK_ICON_SIZE_SMALL_TOOLBAR);

    // Array of pointers. A ragged array of strings because each array of characters is of different length. String is a pointer o the start of the string.
    const char *icon_names[] = {"document-new",
                                "document-save",
                                "edit-undo",
                                "edit-redo",
                                "document-properties",
                                "format-text-bold",
                                "format-text-italic",
                                "gtk-color-picker",
                                "tools-check-spelling",
                                "edit-find"};
    const char *actions[] = {"new_ButtonPress",
                             "save_ButtonPress",
                             "undo_ButtonPress",
                             "redo_ButtonPress",
                             "setup_ButtonPress",
                             "bold_ButtonPress",
                             "italic_ButtonPress",
                             "colorize_ButtonPress",
                             "spelling_ButtonPress",
                             "find_ButtonPress",};
    // Create array of function pointers Syntax: return_type (*name[])(args)
    static void (*callbacks[])(GSimpleAction*, GVariant*, gpointer) = {new_file_callback,
                                                                       save_file_callback,
                                                                       undo_file_callback,
                                                                       redo_file_callback,
                                                                       setup_file_callback,
                                                                       bold_file_callback,
                                                                       italic_file_callback,
                                                                       colorize_file_callback,
                                                                       spelling_file_callback,
                                                                       find_file_callback};
    // Sizeof work because they are pointers of equal size.
    for (int icons = sizeof(icon_names)/sizeof(icon_names[0]) - 1; icons >= 0; icons--) {
        GtkWidget *new_icon = gtk_image_new_from_icon_name(icon_names[icons], GTK_ICON_SIZE_SMALL_TOOLBAR);
        GtkToolItem *new_button = gtk_tool_button_new(new_icon, nullptr);
        gtk_tool_item_set_is_important(new_button, TRUE);
        gtk_toolbar_insert(GTK_TOOLBAR(toolbar), new_button, 0);
        gtk_widget_show(GTK_WIDGET(new_button));
        // win. is needed so gtk knows which map to look into.

        char action_name[50] = {0};
        // An array of strings is [][], sprintf expects a pointer to a string.
        sprintf(action_name, "win.%s", actions[icons]);

        gtk_actionable_set_action_name(GTK_ACTIONABLE(new_button), action_name);
        GSimpleAction *new_file_action = g_simple_action_new(actions[icons], nullptr);
        g_signal_connect(new_file_action, "activate", G_CALLBACK(callbacks[icons]), GTK_WINDOW(window));
        g_action_map_add_action(G_ACTION_MAP(window), G_ACTION(new_file_action));
    }

    gtk_widget_set_hexpand(toolbar, TRUE);
    gtk_widget_show(toolbar);

    // Status bar.
    statusbar = gtk_statusbar_new();

    // Main text field is declared outside of function to be accessible everywhere.
    GtkTextBuffer *buffer = gtk_text_buffer_new(nullptr);
    main_text_field = gtk_text_view_new_with_buffer(buffer);
    create_tags(buffer);
    gtk_text_view_set_wrap_mode(GTK_TEXT_VIEW(main_text_field), GTK_WRAP_WORD);

    GtkWidget *scrolled_window = gtk_scrolled_window_new(nullptr, nullptr);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled_window), GTK_POLICY_AUTOMATIC,
        GTK_POLICY_AUTOMATIC);

    gtk_container_add (GTK_CONTAINER(scrolled_window), main_text_field);
    gtk_container_set_border_width (GTK_CONTAINER(scrolled_window), 0);

    // Assembling all components into main box.
    // Add menu box to the main box.
    gtk_box_pack_start(GTK_BOX(main_box), menu_box, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(main_box), toolbar, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(main_box), scrolled_window, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(main_box), statusbar, FALSE, FALSE, 0);

    gtk_container_add(GTK_CONTAINER(window), main_box);

    gtk_widget_show_all(window);

    update_status();
}

int main (int argc, char **argv) {
    int status = 0;

    GtkApplication *app = gtk_application_new(APP_INTERNAL_NAME, G_APPLICATION_DEFAULT_FLAGS);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);

    return status;
}