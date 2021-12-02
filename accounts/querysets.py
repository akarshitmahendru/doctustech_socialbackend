from django.db.models import QuerySet


class UserOtpQueryMixin(object):
    """ User otp query mixin"""

    def get_user_otp_by_otp_code(self, otp):
        return self.get(otp=otp)

    def get_otp_of_user(self, user):
        return self.get(user=user)

    def get_all_otp_of_user(self, user):
        return self.filter(user=user)

    def get_user_otp_by_otp_and_user(self, otp, user):
        return self.get(otp=otp, user=user)


class UserOtpQuerySet(QuerySet, UserOtpQueryMixin):
    """UserOtp query set"""
    pass
