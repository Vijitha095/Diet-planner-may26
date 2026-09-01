from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


# =========================================================
# USER
# =========================================================

class User(AbstractUser):
    phone = models.CharField(
        max_length=15,
        unique=True
    )

    def __str__(self):
        return self.username


# =========================================================
# PROFILE
# =========================================================

from django.db import models
from django.core.validators import MinValueValidator


class Profile(models.Model):

    GENDER_OPTIONS = (
        ("male", "Male"),
        ("female", "Female"),
        ("others", "Others"),
    )

    ACTIVITY_LEVEL_CHOICES = (
        ("sedentary", "Sedentary"),
        ("light", "Light"),
        ("moderate", "Moderate"),
        ("active", "Active"),
        ("very_active", "Very Active"),
    )

    GOAL_CHOICES = (
        ("weight_loss", "Weight Loss"),
        ("weight_gain", "Weight Gain"),
        ("maintenance", "Maintenance"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile"
    )

    age = models.PositiveIntegerField()

    gender = models.CharField(
        max_length=20,
        choices=GENDER_OPTIONS
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Weight in KG"
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Height in meter"
    )

    target_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )

    activity_level = models.CharField(
        max_length=50,
        choices=ACTIVITY_LEVEL_CHOICES
    )

    goal = models.CharField(
        max_length=30,
        choices=GOAL_CHOICES
    )

    profile_pic = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True
    )

    bmi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False
    )

    bmr = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False
    )

    daily_calorie_goal = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    # -----------------------------------------
    # BMI
    # -----------------------------------------

    def calculate_bmi(self):

        if self.weight and self.height:

            weight = float(self.weight)
            height = float(self.height)

            return round(
                weight / (height ** 2),
                2
            )

        return None

    # -----------------------------------------
    # BMR
    # -----------------------------------------

    def calculate_bmr(self):

        weight = float(self.weight)

        # Height is stored in meter
        # Convert meter to centimeter
        height_cm = float(self.height) * 100

        age = self.age

        if self.gender == "male":

            bmr = (
                (10 * weight)
                + (6.25 * height_cm)
                - (5 * age)
                + 5
            )

        else:

            bmr = (
                (10 * weight)
                + (6.25 * height_cm)
                - (5 * age)
                - 161
            )

        return round(bmr)

    # -----------------------------------------
    # DAILY CALORIE GOAL
    # -----------------------------------------

    def calculate_daily_calories(self):

        bmr = self.calculate_bmr()

        activity_factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }

        # Calculate maintenance calories
        maintenance = (
            bmr * activity_factors[self.activity_level]
        )

        # Adjust according to goal

        if self.goal == "weight_loss":

            calories = maintenance - 500

        elif self.goal == "weight_gain":

            calories = maintenance + 300

        else:

            calories = maintenance

        return round(calories)

    # -----------------------------------------
    # SAVE
    # -----------------------------------------

    def save(self, *args, **kwargs):

        # Calculate BMI
        self.bmi = self.calculate_bmi()

        # Calculate BMR
        self.bmr = self.calculate_bmr()

        # Calculate daily calorie goal
        self.daily_calorie_goal = self.calculate_daily_calories()

        super().save(*args, **kwargs)

    # -----------------------------------------
    # STRING
    # -----------------------------------------

    def __str__(self):

        return f"{self.user.username} profile"