class Table:

    def __init__(self):
        self.rows = []
        self.fmt = None

    def add(self, *values):
        self.rows.append(values)

    def print_row(self, vals):
        vals_cast_str = [str(val) for val in vals]
        print(self.fmt.format(*vals_cast_str))

    def prepare_format(self):
        max_width = [0] * len(self.rows[0])
        for row in self.rows:
            for i, col in enumerate(row):
                if col is not None:
                    max_width[i] = max(max_width[i], len(col))
        for mw in max_width:
            if self.fmt:
                self.fmt += "  "
            else:
                self.fmt = ""
            self.fmt += "{:" + str(mw) + "}"

    def print(self, distinct=False):
        self.prepare_format()
        rows_sorted = sorted(self.rows[1:], key=lambda val: val[0])
        self.print_row(self.rows[0])
        prev_row = None
        for row in rows_sorted:
            if distinct and prev_row == row:
                continue
            self.print_row(row)
            prev_row = row
