from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    all = {}  # Cache: id -> Review instance

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review id={self.id} year={self.year} "
            f"summary={self.summary!r} employee_id={self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id:
            self.update()
        else:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id)
            )
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        return self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        return review.save()

    @classmethod
    def instance_from_db(cls, row):
        id_, year, summary, employee_id = row
        if id_ in cls.all:
            inst = cls.all[id_]
            inst.year = year
            inst.summary = summary
            inst.employee_id = employee_id
        else:
            inst = cls(year, summary, employee_id, id=id_)
            cls.all[id_] = inst
        return inst

    @classmethod
    def find_by_id(cls, id_):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id_,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee_id, self.id)
        )
        CONN.commit()
        return self

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        if self.id in Review.all:
            Review.all.pop(self.id)
        self.id = None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property validation
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, val):
        if not isinstance(val, int) or val < 2000:
            raise ValueError("year must be an integer ≥ 2000")
        self._year = val

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, val):
        if not isinstance(val, str) or not val.strip():
            raise ValueError("summary must be a non-empty string")
        self._summary = val

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, val):
        from lib.employee import Employee
        if not isinstance(val, int) or Employee.find_by_id(val) is None:
            raise ValueError("employee_id must reference an existing Employee")
        self._employee_id = val



















