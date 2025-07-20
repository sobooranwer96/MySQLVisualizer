import tkinter as tk
import db_connector

class MySQLVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MySQL Visualizer")
        self.master.geometry("1000x800")

        self.host_var = tk.StringVar(value="localhost")
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_label = None

        self.db_connection = None
        self.selected_db_var = tk.StringVar(self.master)
        self.database_options_menu = None
        
        self.foreign_keys = [] 
        self.table_positions = {}

        self.connection_frame = self._create_connection_frame()
        self.connection_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.canvas_frame = self._create_canvas_frame()

    def _create_connection_frame(self):
        frame = tk.Frame(self.master)

        host_label = tk.Label(frame, text="Host:", font=("Arial", 12, "bold"))
        host_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        host_entry = tk.Entry(frame, textvariable=self.host_var)
        host_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        username_label = tk.Label(frame, text="Username:", font=("Arial", 12, "bold"))
        username_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        username_entry = tk.Entry(frame, textvariable=self.username_var)
        username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        password_label = tk.Label(frame, text="Password:", font=("Arial", 12, "bold"))
        password_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        password_entry = tk.Entry(frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.status_label = tk.Label(frame, text="", font=("Arial", 12), fg="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5, sticky="w")

        connect_button = tk.Button(frame, text="Connect", font=("Arial", 12, "bold"), command=self._on_connect_button_click)
        connect_button.grid(row=3, column=1, padx=5, pady=5, sticky="e")

        frame.grid_columnconfigure(1, weight=1)

        return frame

    def _create_canvas_frame(self):
        frame = tk.Frame(self.master)

        self.canvas = tk.Canvas(frame, width=1000, height=600, bg="lightgray", bd=2, relief="groove")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        db_select_label = tk.Label(frame, text="Select Database:", font=("Arial", 12))
        db_select_label.pack(pady=5)

        self.selected_db_var.set("No Database Selected")
        self.database_options_menu = tk.OptionMenu(frame, self.selected_db_var, "No Database Selected")
        self.database_options_menu.pack(pady=5)

        load_schema_button = tk.Button(frame, text="Load Schema", font=("Arial", 12, "bold"), command=self._on_load_schema_button_click)
        load_schema_button.pack(pady=5)

        return frame

    def _populate_database_dropdown(self):
        """Fetches database names and populates the dropdown menu."""
        if self.db_connection:
            try:
                databases = db_connector.get_all_databases(self.db_connection)

                menu = self.database_options_menu["menu"]
                menu.delete(0, "end")

                if databases:
                    for db in databases:
                        menu.add_command(label=db, command=tk._setit(self.selected_db_var, db))
                    self.selected_db_var.set(databases[0])
                else:
                    self.selected_db_var.set("No Databases Found")
                    menu.add_command(label="No Databases Found", command=tk._setit(self.selected_db_var, "No Databases Found"))

            except Exception as e:
                self.status_label.config(text=f"Error fetching databases: {e}", fg="red")
        else:
            self.status_label.config(text="Not connected to database.", fg="orange")
            
    def _on_connect_button_click(self):
        host = self.host_var.get()
        username = self.username_var.get()
        password = self.password_var.get()

        self.status_label.config(text="Connecting...", fg="blue")
        self.master.update_idletasks()

        try:
            self.db_connection = db_connector.connect(host, username, password)
            
            if self.db_connection:
                self.status_label.config(text="Connection successful!", fg="green")

                self.connection_frame.pack_forget()
                self.canvas_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

                self._populate_database_dropdown()

            else:
                self.status_label.config(text="Connection failed. Check credentials and server status.", fg="red")

        except Exception as e:
            self.status_label.config(text=f"An unexpected error occurred: {e}", fg="red")
    
    def _on_load_schema_button_click(self):
        """Handles the 'Load Schema' button click event."""
        selected_db = self.selected_db_var.get()

        if not self.db_connection:
            self.status_label.config(text="Error: Not connected to a database.", fg="red")
            return

        if selected_db == "No Database Selected" or not selected_db:
            self.status_label.config(text="Please select a database.", fg="orange")
            return

        self.status_label.config(text=f"Loading schema for '{selected_db}'...", fg="blue")
        self.master.update_idletasks()

        self.canvas.delete("all") 
        self.table_positions = {}

        try:
            db_schema, foreign_keys = db_connector.get_schema_for_database(self.db_connection, selected_db)
            self.foreign_keys = foreign_keys

            if db_schema:
                self.status_label.config(text=f"Schema loaded for '{selected_db}'.", fg="green")
                
                x_offset = 50
                y_offset = 50
                current_x = x_offset
                current_y = y_offset
                row_max_height = 0 # To track the tallest table in the current row

                for table_name, columns in db_schema.items():
                    x1, y1, x2, y2 = self._draw_table(table_name, columns, current_x, current_y)
                    
                    self.table_positions[table_name] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}

                    table_width = x2 - x1
                    table_height = y2 - y1

                    if table_height > row_max_height:
                        row_max_height = table_height

                    current_x += table_width + 30 # Move right by table width + spacing

                    # Check if the next table would go off screen
                    if current_x + 250 > self.canvas.winfo_width() and len(db_schema) > 1: # 250 is an estimated min table width
                        current_x = x_offset
                        current_y += row_max_height + 30 # Move to next row, based on tallest table in previous row
                        row_max_height = 0 # Reset max height for new row
                
                self.canvas.update_idletasks() 
                
                self._draw_relationships()


            else:
                self.status_label.config(text=f"No schema found for '{selected_db}'.", fg="orange")

        except Exception as e:
            self.status_label.config(text=f"Error loading schema: {e}", fg="red")

    def _draw_table(self, table_name, columns, x, y):
        """
        Draws a single table rectangle with its name and columns on the canvas.
        Returns the (x1, y1, x2, y2) coordinates of the drawn table.
        """
        # Define styling constants
        TABLE_HEADER_HEIGHT = 30
        COLUMN_LINE_HEIGHT = 20
        TEXT_PADDING = 15 
        RECT_PADDING = 10

        # Calculate table width based on longest text
        font_table_name = ("Arial", 14, "bold")
        font_column = ("Arial", 10)

        # Measure table name width
        dummy_text_id = self.canvas.create_text(0, 0, text=table_name, font=font_table_name, anchor="nw", state="hidden")
        bbox = self.canvas.bbox(dummy_text_id)
        table_name_width = bbox[2] - bbox[0] if bbox else 0
        self.canvas.delete(dummy_text_id)

        max_content_width = table_name_width

        # Calculate width needed for columns
        for col in columns:
            col_display_string = self._format_column_display(table_name, col) 
            dummy_text_id = self.canvas.create_text(0, 0, text=col_display_string, font=font_column, anchor="nw", state="hidden")
            bbox = self.canvas.bbox(dummy_text_id)
            column_text_width = bbox[2] - bbox[0] if bbox else 0
            self.canvas.delete(dummy_text_id)
            if column_text_width > max_content_width:
                max_content_width = column_text_width
        
        table_width = max_content_width + (2 * RECT_PADDING) + (2 * TEXT_PADDING)
        
        if table_width < 250:
            table_width = 250

        # Calculate table height
        table_height = TABLE_HEADER_HEIGHT + (len(columns) * COLUMN_LINE_HEIGHT) + (2 * RECT_PADDING)

        # Define rectangle coordinates
        x1, y1 = x, y
        x2, y2 = x + table_width, y + table_height

        # Draw the table rectangle
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=2, tags=(table_name, "table_box"))

        # Draw table name
        table_name_x = x1 + table_width / 2
        table_name_y = y1 + TABLE_HEADER_HEIGHT / 2
        self.canvas.create_text(table_name_x, table_name_y, text=table_name, font=font_table_name, fill="navy", tags=(table_name, "table_name"))

        # Draw columns
        current_y_for_column = y1 + TABLE_HEADER_HEIGHT + RECT_PADDING
        for col in columns:
            col_display_string = self._format_column_display(table_name, col)
            self.canvas.create_text(x1 + TEXT_PADDING, current_y_for_column, text=col_display_string, 
                                    font=font_column, anchor="nw", fill="black", tags=(table_name, "column", f"{table_name}_{col['name']}"))
            current_y_for_column += COLUMN_LINE_HEIGHT

        # Return the coordinates of the drawn table
        return x1, y1, x2, y2

    def _format_column_display(self, table_name, column_info):
        """Helper to format column display string"""
        name = column_info['name']
        data_type = column_info['type'].upper()
        
        if column_info['length'] is not None and column_info['length'] != 0:
            data_type += f"({column_info['length']})"
        
        key_info_parts = []
        if column_info['key'] == 'PRI':
            key_info_parts.append("[PK]")
        elif column_info['key'] == 'UNI':
            key_info_parts.append("[UN]")

        is_fk = False
        if self.foreign_keys:
            for fk in self.foreign_keys:
                if fk['fk_table'] == table_name and fk['fk_column'] == name:
                    is_fk = True
                    break
        if is_fk:
            key_info_parts.append("[FK]")

        key_info = "".join(key_info_parts)

        display_string = f"{name} ({data_type})"
        if key_info:
            display_string += f" {key_info}"
        
        return display_string
    
    def _draw_relationships(self):
        """Draws lines connecting foreign key columns to their referenced primary key columns."""
        if not self.db_connection or not self.foreign_keys:
            return

        for fk in self.foreign_keys:
            fk_table = fk['fk_table']
            fk_column = fk['fk_column']
            pk_table = fk['pk_table']
            pk_column = fk['pk_column']

            # Ensure both tables are drawn on the canvas and their positions are known
            if fk_table in self.table_positions and pk_table in self.table_positions:
                # Get the bounding box of the foreign key column text
                # Use tags to identify column text"
                fk_column_item_id = self.canvas.find_withtag(f"{fk_table}_{fk_column}")
                
                # Get the bounding box of the primary key column text
                pk_column_item_id = self.canvas.find_withtag(f"{pk_table}_{pk_column}")

                if fk_column_item_id and pk_column_item_id:
                    # Get coordinates of the column text items
                    fk_bbox = self.canvas.bbox(fk_column_item_id[0]) 
                    pk_bbox = self.canvas.bbox(pk_column_item_id[0])

                    if fk_bbox and pk_bbox:
                        # Calculate midpoints of the right side of FK column and left side of PK column
                        # This creates a line from the FK column to the PK column
                        start_x = fk_bbox[2] # Right edge of FK column text
                        start_y = (fk_bbox[1] + fk_bbox[3]) / 2 # Mid-height of FK column text

                        end_x = pk_bbox[0] # Left edge of PK column text
                        end_y = (pk_bbox[1] + pk_bbox[3]) / 2 # Mid-height of PK column text

                        # Draw the line
                        self.canvas.create_line(start_x, start_y, end_x, end_y, 
                                                fill="blue", width=2, arrow=tk.LAST,
                                                tags=("relationship", f"fk_{fk_table}_{fk_column}_to_{pk_table}_{pk_column}"))
                else:
                    print(f"Warning: Could not find canvas items for FK {fk_table}.{fk_column} or PK {pk_table}.{pk_column}. This might happen if columns are not visible or tags are incorrect.")
            else:
                print(f"Warning: Table positions not found for FK table '{fk_table}' or PK table '{pk_table}'. Ensure tables are drawn.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MySQLVisualizerApp(root)
    root.mainloop()
