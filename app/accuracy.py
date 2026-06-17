def calculate_accuracy(
        template,
        max_angle,
        min_angle,
        mobility_limit=None
):

    if template == "elbow_flexion":

        if mobility_limit:

            target_top = mobility_limit

        else:

            target_top = 50

        score_top = max(
            0,
            100 - abs(min_angle - target_top)
        )

        score_bottom = max(
            0,
            100 - abs(max_angle - 160)
        )

        return round(
            (score_top + score_bottom) / 2
        )

    return 100