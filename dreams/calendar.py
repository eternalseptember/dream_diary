import calendar
calendar.setfirstweekday(calendar.SUNDAY)
from django.db.models.functions import ExtractMonth, ExtractDay
from django.urls import reverse


class BlogHTMLCalendar(calendar.Calendar):
    def __init__(self, year, dreams_list):
        self.year = year
        self.dreams_list = dreams_list
        self.month_list = self.get_monthly_tally()


    def get_monthly_tally(self):
        """
        Creates a list of months that have posts in them.
        Monthly_tally isn't being used currently, but can be.
        Mostly useful in the early part of the year.
        """
        monthly_tally = self.dreams_list \
            .order_by("created_on") \
            .values(month=ExtractMonth("created_on")) \
            .order_by("month") \
            .distinct()

        month_list = [query_pair["month"] for query_pair in monthly_tally]
        return month_list


    def printyear(self):
        """
        Formats and prints a yearly calendar: 3 months per row x 4 rows.
        The year is set as a class variable when this object is created.
        """
        month_counter = 1
        cal_html = '<table class="year" border="0" cellpadding="0" cellspacing="0">'

        # Yearly archive link
        cal_html += '<tr><th class="year" colspan="3">'
        cal_html += self.get_yearly_archive_link()
        cal_html += '</th></tr>'

        # Three months per row; four rows per year.
        for calendar_rows in range(4):
            cal_html += '<tr>'

            # Each month table inside its own <td>.
            for cal_row_month in range(3):
                cal_html += '<td>'
                cal_html += self.print_month(month_counter)  # Format the monthly calendar here.
                month_counter += 1  # Next month.
                cal_html += '</td>'

            cal_html += '</tr>'

        cal_html += '</table>'
        return cal_html


    def get_yearly_archive_link(self):
        """
        Format and prints the year with a link to that year's archives.
        """
        yearly_archive_url = reverse("archive_year", args=[self.year])
        return '<a href="{}"><h3>{}</h3></a>'.format(yearly_archive_url, self.year)
    

    def print_month(self, month):
        """
        Formats and prints a monthly calendar.
        Month name is a link to that month's archives, if there are posts that month.
        Day is a link to that day's archives, if there are posts that day.
        """
        month_html = '<table class="month" border="0" cellpadding="0" cellspacing="0">'

        # Monthly archive link
        month_html += '<tr><th class="month" colspan="7">'
        month_url, posts_this_month = self.get_monthly_archive_link(month)
        month_html += month_url
        month_html += '</th></tr>'

        # Week header
        month_html += '<tr>'
        month_html += '<th class="day_of_the_week">Sun</th>'
        month_html += '<th class="day_of_the_week">Mon</th>'
        month_html += '<th class="day_of_the_week">Tue</th>'
        month_html += '<th class="day_of_the_week">Wed</th>'
        month_html += '<th class="day_of_the_week">Thu</th>'
        month_html += '<th class="day_of_the_week">Fri</th>'
        month_html += '<th class="day_of_the_week">Sat</th>'
        month_html += '</tr>'

        # Weeks of the month
        weeks_of_the_month = calendar.monthcalendar(self.year, month)

        # List of days that have posts
        if posts_this_month:
            daily_posts = self.get_daily_posts_per_month(month)

        for week in weeks_of_the_month:
            month_html += '<tr>'

            for day in week:
                # Beginning <td> is set individually per cell, depending on whether there's a post that day.
                if day == 0:
                    month_html += '<td class="day_of_the_month">&nbsp;'
                else:
                    # Link to the day's archives if there are posts this month.
                    if posts_this_month:
                        month_html += self.get_daily_archive_link(daily_posts, month, day)
                    else:
                        month_html += '<td class="day_of_the_month">' + str(day)

                month_html += '</td>'

            month_html += '</tr>'

        month_html += '</table>'
        return month_html


    def get_monthly_archive_link(self, month):
        """
        Formats and prints a monthly calendar header.
        Month name is a link to that month's archives, if there are posts that month.
        """
        if month in self.month_list:
            monthly_archive_url = reverse("archive_month", args=[self.year, month])
            return '<a href="{}">{}</a>'.format(monthly_archive_url, calendar.month_name[month]), True
        else:
            return str(calendar.month_name[month]), False


    def get_daily_posts_per_month(self, month):
        """
        Creates a list of days in a month that have posts in them.
        Daily_tally isn't being used currently, but can be.
        Mostly useful in the early part of the month.
        """
        daily_tally = self.dreams_list \
            .filter(created_on__month = month) \
            .values(day=ExtractDay("created_on")) \
            .order_by("day") \
            .distinct()
        
        daily_list = [query_pair["day"] for query_pair in daily_tally]
        return daily_list


    def get_daily_archive_link(self, daily_posts, month, day):
        """
        If there's a post on this day, then create a link to that day's archives.
        Beginning <td> is set individually per cell,
        depending on whether there's a post that day.
        """
        if day in daily_posts:
            daily_archive_url = reverse("archive_day", args=[self.year, month, day])
            return '<td class="day_of_the_month daily_link"><a href="{}">{}</a>'\
                .format(daily_archive_url, day)
        else:
            return '<td class="day_of_the_month">' + str(day)




