import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "exercisecoach.db"

EXERCISES = [

    # ==========================
    # NO EQUIPMENT
    # ==========================

    ("Push-ups", "Upper Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Chest, shoulders, arms, and core

STARTING POSITION:
Place your hands on the floor slightly wider than shoulder-width apart. Extend your legs behind you and keep your body in a straight line from head to heels.

MOVEMENT:
Slowly bend your elbows to lower your chest towards the floor. Push through your hands to return to the starting position.

IMPORTANT TIPS:
Keep your core tight and your back straight. Do not let your hips drop or lift too high.

BREATHING:
Breathe in as you lower your body, and breathe out as you push up.
""", "Intermediate", 0),

    ("Pike Push-ups", "Upper Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Shoulders, arms, and upper chest

STARTING POSITION:
Start with your hands and feet on the floor. Lift your hips up so your body forms an upside-down V shape.

MOVEMENT:
Bend your elbows and lower the top of your head towards the floor, then push back up to the starting position.

IMPORTANT TIPS:
Keep your hips lifted and your movements controlled. Do not rush through the motion.

BREATHING:
Breathe in as you lower down, and breathe out as you push back up.
""", "Advanced", 0),

    ("Wall Push-ups", "Upper Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Chest, shoulders, and arms

STARTING POSITION:
Stand facing a wall and place your hands flat against the wall at shoulder height.

MOVEMENT:
Bend your elbows to bring your chest closer to the wall. Push back until your arms are straight again.

IMPORTANT TIPS:
Keep your body in a straight line and avoid bending at the waist.

BREATHING:
Breathe in as you move towards the wall, and breathe out as you push away.
""", "Beginner", 1),

    ("Tricep dips (chair/bench)", "Upper Body",
"""EQUIPMENT REQUIRED:
Stable chair or bench

TARGET AREA:
Triceps, shoulders, and chest

STARTING POSITION:
Sit on the edge of a chair or bench. Place your hands beside your hips and slide your body forward off the seat.

MOVEMENT:
Lower your body by bending your elbows, then push back up until your arms are straight.

IMPORTANT TIPS:
Keep your back close to the chair or bench. Do not let your shoulders shrug up.

BREATHING:
Breathe in as you lower down, and breathe out as you push up.
""", "Intermediate", 1),

    ("Plank shoulder taps", "Upper Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Shoulders, arms, and core

STARTING POSITION:
Start in a high plank position with your hands on the floor and your body in a straight line.

MOVEMENT:
Lift one hand and tap the opposite shoulder. Return that hand to the floor and repeat on the other side.

IMPORTANT TIPS:
Keep your hips as still as possible. Avoid rocking side to side.

BREATHING:
Breathe steadily throughout the movement.
""", "Intermediate", 0),

    ("Squats", "Lower Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Thighs, glutes, and hips

STARTING POSITION:
Stand upright with your feet shoulder-width apart and your arms relaxed or held in front of you.

MOVEMENT:
Slowly bend your knees and push your hips back as if sitting on a chair. Return to standing by pushing through your feet.

IMPORTANT TIPS:
Keep your chest lifted and your back straight. Make sure your knees follow the direction of your toes.

BREATHING:
Breathe in as you lower down, and breathe out as you stand up.
""", "Beginner", 1),

    ("Lunges", "Lower Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Thighs, glutes, and hips

STARTING POSITION:
Stand upright with your feet together.

MOVEMENT:
Step one foot forward and lower your body until both knees bend comfortably. Push back to the starting position and repeat on the other side.

IMPORTANT TIPS:
Keep your upper body upright and your front knee aligned with your foot.

BREATHING:
Breathe in as you lower down, and breathe out as you push back up.
""", "Intermediate", 0),

    ("Step-ups", "Lower Body",
"""EQUIPMENT REQUIRED:
Step, stair, or sturdy low platform

TARGET AREA:
Thighs, glutes, and calves

STARTING POSITION:
Stand facing the step or platform with your feet hip-width apart.

MOVEMENT:
Place one foot on the step and push through it to lift your body up. Step back down slowly and repeat.

IMPORTANT TIPS:
Use a low step if you are a beginner. Keep your movement controlled and avoid pushing off too much with the lower foot.

BREATHING:
Breathe out as you step up, and breathe in as you step down.
""", "Beginner", 1),

    ("Glute bridges", "Lower Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Glutes, hamstrings, and core

STARTING POSITION:
Lie on your back with your knees bent and your feet flat on the floor.

MOVEMENT:
Lift your hips until your body forms a straight line from shoulders to knees. Lower your hips back down slowly.

IMPORTANT TIPS:
Do not arch your lower back too much. Focus on squeezing your glutes at the top.

BREATHING:
Breathe out as you lift your hips, and breathe in as you lower them.
""", "Beginner", 1),

    ("Calf raises", "Lower Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Calves and ankles

STARTING POSITION:
Stand upright with your feet hip-width apart. Hold onto a wall or chair if needed for balance.

MOVEMENT:
Lift your heels off the floor so you rise onto your toes. Lower your heels back down slowly.

IMPORTANT TIPS:
Move slowly and keep your weight balanced. Do not bounce.

BREATHING:
Breathe out as you lift up, and breathe in as you lower down.
""", "Beginner", 1),

    ("Plank", "Core",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Core, shoulders, and back

STARTING POSITION:
Place your forearms on the floor and extend your legs behind you. Keep your body in a straight line.

MOVEMENT:
Hold the position while keeping your core engaged.

IMPORTANT TIPS:
Do not let your hips sag or lift too high. Keep your neck relaxed and look down.

BREATHING:
Breathe steadily and naturally throughout the hold.
""", "Beginner", 1),

    ("Side plank", "Core",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Core, obliques, and shoulders

STARTING POSITION:
Lie on one side and place your forearm under your shoulder. Stack your legs and lift your hips off the floor.

MOVEMENT:
Hold your body in a straight line while balancing on your forearm and side of your foot.

IMPORTANT TIPS:
Keep your hips lifted and your shoulder stable. If needed, bend your lower knee for support.

BREATHING:
Breathe steadily throughout the hold.
""", "Intermediate", 1),

    ("Mountain climbers", "Core",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Core, shoulders, and legs

STARTING POSITION:
Start in a high plank position with your hands on the floor.

MOVEMENT:
Bring one knee towards your chest, return it, then repeat with the other knee in a running motion.

IMPORTANT TIPS:
Keep your hands firmly planted and your body stable. Move at a pace you can control.

BREATHING:
Breathe steadily throughout the exercise.
""", "Intermediate", 0),

    ("Bicycle crunches", "Core",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Core and obliques

STARTING POSITION:
Lie on your back with your hands lightly behind your head and your knees bent.

MOVEMENT:
Lift your shoulders off the floor and bring one elbow towards the opposite knee while extending the other leg. Alternate sides.

IMPORTANT TIPS:
Do not pull on your neck. Move slowly and focus on the twist.

BREATHING:
Breathe out during each twist, and breathe in as you switch sides.
""", "Intermediate", 1),

    ("Leg raises", "Core",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Lower abs and hip flexors

STARTING POSITION:
Lie flat on your back with your legs straight.

MOVEMENT:
Lift both legs upwards together as high as comfortable, then lower them slowly without dropping them.

IMPORTANT TIPS:
Keep your lower back as close to the floor as possible. Bend your knees slightly if needed.

BREATHING:
Breathe out as you lift your legs, and breathe in as you lower them.
""", "Beginner", 1),

    ("Russian twists (bodyweight)", "Core",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Core and obliques

STARTING POSITION:
Sit on the floor with your knees bent and your feet on the floor or slightly lifted.

MOVEMENT:
Lean back slightly and rotate your upper body from side to side.

IMPORTANT TIPS:
Keep your spine long and your movement controlled. Do not twist too quickly.

BREATHING:
Breathe out as you twist to each side, and breathe in as you return through the centre.
""", "Beginner", 1),

    ("Burpees", "Full Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Full body, especially legs, chest, arms, and core

STARTING POSITION:
Stand upright with your feet shoulder-width apart.

MOVEMENT:
Lower into a squat, place your hands on the floor, jump your feet back into a plank, return your feet in, and jump up.

IMPORTANT TIPS:
Perform each part of the movement with control. Beginners may remove the jump if needed.

BREATHING:
Breathe steadily throughout the movement.
""", "Advanced", 0),

    ("Jump squats", "Full Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Legs, glutes, and calves

STARTING POSITION:
Stand with your feet shoulder-width apart.

MOVEMENT:
Lower into a squat, then push through your feet to jump upwards. Land softly and return into the next squat.

IMPORTANT TIPS:
Keep your knees aligned with your toes. Land gently to reduce impact.

BREATHING:
Breathe in as you lower, and breathe out as you jump.
""", "Advanced", 0),

    ("High knees", "Full Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Legs, core, and cardiovascular endurance

STARTING POSITION:
Stand upright with your feet hip-width apart.

MOVEMENT:
Run in place while lifting your knees as high as comfortable.

IMPORTANT TIPS:
Keep your upper body tall and use your arms naturally. Move at a pace that is safe for you.

BREATHING:
Breathe steadily throughout the exercise.
""", "Intermediate", 0),

    ("Bear crawl", "Full Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Shoulders, arms, core, and legs

STARTING POSITION:
Start on your hands and feet with your knees slightly lifted off the floor.

MOVEMENT:
Move one hand and the opposite foot forward, then alternate sides while staying low.

IMPORTANT TIPS:
Keep your back flat and your movements controlled. Avoid rushing.

BREATHING:
Breathe steadily as you move.
""", "Advanced", 0),

    ("Skaters", "Full Body",
"""EQUIPMENT REQUIRED:
No equipment

TARGET AREA:
Legs, glutes, and cardiovascular endurance

STARTING POSITION:
Stand upright with your feet hip-width apart.

MOVEMENT:
Jump sideways from one foot to the other, swinging the opposite leg behind you.

IMPORTANT TIPS:
Land softly and keep your balance controlled. Reduce the jump size if needed.

BREATHING:
Breathe steadily throughout the exercise.
""", "Intermediate", 0),

    # ==========================
    # RESISTANCE BAND
    # ==========================

    ("Band rows", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Back, shoulders, and arms

STARTING POSITION:
Hold the resistance band with both hands and extend your arms in front of you.

MOVEMENT:
Pull the band towards your body by bending your elbows. Slowly return to the starting position.

IMPORTANT TIPS:
Keep your back straight and squeeze your shoulder blades together.

BREATHING:
Breathe out as you pull, and breathe in as you return.
""", "Beginner", 1),

    ("Band chest press", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Chest, shoulders, and arms

STARTING POSITION:
Hold the band handles or ends at chest level with your elbows bent.

MOVEMENT:
Press your hands forward until your arms are straight, then return slowly.

IMPORTANT TIPS:
Keep your chest lifted and avoid shrugging your shoulders.

BREATHING:
Breathe out as you press forward, and breathe in as you return.
""", "Beginner", 1),

    ("Band shoulder press", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Shoulders and arms

STARTING POSITION:
Hold the resistance band at shoulder level with your elbows bent.

MOVEMENT:
Press your hands upwards until your arms are extended, then lower slowly.

IMPORTANT TIPS:
Do not force your arms too high if it feels uncomfortable. Keep the movement within a safe range.

BREATHING:
Breathe out as you press up, and breathe in as you lower.
""", "Beginner", 1),

    ("Band lateral raises", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Shoulders

STARTING POSITION:
Stand or sit upright while holding the band ends with your hands by your sides.

MOVEMENT:
Lift both arms out to the sides until they reach shoulder level, then lower slowly.

IMPORTANT TIPS:
Keep your elbows slightly soft and avoid lifting your shoulders.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Beginner", 1),

    ("Band bicep curls", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Biceps and forearms

STARTING POSITION:
Stand on the band and hold both ends in your hands with your arms by your sides.

MOVEMENT:
Bend your elbows to curl your hands towards your shoulders. Lower them slowly.

IMPORTANT TIPS:
Keep your elbows close to your body and avoid swinging.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Beginner", 1),

    ("Band tricep extensions", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Triceps

STARTING POSITION:
Hold the band securely and position your arms so you can extend them against resistance.

MOVEMENT:
Straighten your elbows to extend your arms, then return slowly.

IMPORTANT TIPS:
Keep your upper arms as still as possible.

BREATHING:
Breathe out as you extend, and breathe in as you return.
""", "Beginner", 1),

    ("Face pulls", "Upper Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Upper back, rear shoulders, and arms

STARTING POSITION:
Hold the band with both hands at shoulder height.

MOVEMENT:
Pull the band towards your face while bending your elbows outwards. Return slowly.

IMPORTANT TIPS:
Keep your chest lifted and squeeze your shoulder blades together.

BREATHING:
Breathe out as you pull, and breathe in as you return.
""", "Intermediate", 1),

    ("Band squats", "Lower Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Thighs, glutes, and hips

STARTING POSITION:
Place the band in position and stand upright with your feet shoulder-width apart.

MOVEMENT:
Lower into a squat and return to standing.

IMPORTANT TIPS:
Keep your knees aligned with your toes and maintain tension in the band.

BREATHING:
Breathe in as you lower down, and breathe out as you stand up.
""", "Beginner", 1),

    ("Lateral band walks", "Lower Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Glutes, hips, and thighs

STARTING POSITION:
Place the band around your legs and stand in a slight squat position.

MOVEMENT:
Step sideways one foot at a time while keeping tension in the band.

IMPORTANT TIPS:
Take small controlled steps and keep your hips level.

BREATHING:
Breathe steadily throughout the movement.
""", "Beginner", 1),

    ("Glute kickbacks", "Lower Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Glutes and hamstrings

STARTING POSITION:
Stand upright while holding onto support if needed, with the band placed for resistance.

MOVEMENT:
Extend one leg backwards in a controlled motion, then return it to the starting position.

IMPORTANT TIPS:
Keep your upper body stable and avoid arching your lower back.

BREATHING:
Breathe out as you kick back, and breathe in as you return.
""", "Beginner", 1),

    ("Hip thrusts with band", "Lower Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Glutes, hips, and hamstrings

STARTING POSITION:
Sit with your upper back supported and the band positioned for resistance.

MOVEMENT:
Lift your hips upwards until your body forms a straight line, then lower slowly.

IMPORTANT TIPS:
Squeeze your glutes at the top and keep your knees controlled.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Beginner", 1),

    ("Hamstring curls (band)", "Lower Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Hamstrings

STARTING POSITION:
Position the band so it provides resistance while your leg bends at the knee.

MOVEMENT:
Bend your knee to bring your heel closer towards you, then return slowly.

IMPORTANT TIPS:
Move slowly and keep your hips stable.

BREATHING:
Breathe out as you curl, and breathe in as you return.
""", "Beginner", 1),

    ("Monster walks", "Lower Body",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Glutes, hips, and thighs

STARTING POSITION:
Place the band around your legs and stand in a slight squat position.

MOVEMENT:
Step diagonally forward and continue walking in a controlled pattern.

IMPORTANT TIPS:
Keep tension in the band at all times and avoid standing fully upright.

BREATHING:
Breathe steadily throughout the exercise.
""", "Beginner", 1),

    ("Pallof press", "Core",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Core and trunk stability

STARTING POSITION:
Stand or sit upright while holding the band at chest level.

MOVEMENT:
Press your hands straight forward and hold briefly, then bring them back in.

IMPORTANT TIPS:
Keep your body from twisting and stay stable through your trunk.

BREATHING:
Breathe out as you press forward, and breathe in as you return.
""", "Intermediate", 1),

    ("Band woodchoppers", "Core",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Core, shoulders, and obliques

STARTING POSITION:
Hold the band with both hands and prepare for a diagonal pulling motion.

MOVEMENT:
Pull the band diagonally across your body in a controlled chopping action, then return slowly.

IMPORTANT TIPS:
Rotate through your upper body with control and avoid jerking the movement.

BREATHING:
Breathe out as you pull across, and breathe in as you return.
""", "Intermediate", 1),

    ("Standing anti-rotation hold", "Core",
"""EQUIPMENT REQUIRED:
Resistance band

TARGET AREA:
Core and trunk stability

STARTING POSITION:
Stand upright holding the resistance band at chest level.

MOVEMENT:
Hold the band steady in front of your chest and resist being pulled to one side.

IMPORTANT TIPS:
Keep your body still and your core engaged.

BREATHING:
Breathe steadily throughout the hold.
""", "Intermediate", 1),

    # ==========================
    # DUMBBELL / KETTLEBELL
    # ==========================

    ("Dumbbell bench press", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells and bench

TARGET AREA:
Chest, shoulders, and arms

STARTING POSITION:
Lie or sit on a bench while holding a dumbbell in each hand at chest level.

MOVEMENT:
Press the dumbbells upwards until your arms are straight, then lower them slowly.

IMPORTANT TIPS:
Keep your wrists stable and do not rush the lowering phase.

BREATHING:
Breathe out as you press up, and breathe in as you lower.
""", "Intermediate", 1),

    ("Shoulder press", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Shoulders and arms

STARTING POSITION:
Hold the weights at shoulder level with your elbows bent.

MOVEMENT:
Press the weights upwards until your arms are extended, then lower them slowly.

IMPORTANT TIPS:
Do not lock your elbows and keep the movement within a comfortable range.

BREATHING:
Breathe out as you press up, and breathe in as you lower.
""", "Intermediate", 1),

    ("Lateral raises", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Shoulders

STARTING POSITION:
Stand or sit upright with the weights by your sides.

MOVEMENT:
Lift your arms out to the sides until shoulder height, then lower slowly.

IMPORTANT TIPS:
Keep the weights light enough to move with control. Avoid shrugging.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Beginner", 1),

    ("Bent-over rows", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Back, shoulders, and arms

STARTING POSITION:
Hold the weights in your hands and hinge forward slightly at the hips with your back straight.

MOVEMENT:
Pull the weights towards your torso, then lower them slowly.

IMPORTANT TIPS:
Keep your back straight and avoid jerking the weights.

BREATHING:
Breathe out as you pull, and breathe in as you lower.
""", "Intermediate", 1),

    ("Bicep curls", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Biceps and forearms

STARTING POSITION:
Hold a weight in each hand with your arms by your sides and palms facing forward.

MOVEMENT:
Slowly bend your elbows to lift the weights towards your shoulders. Lower them back down in a controlled motion.

IMPORTANT TIPS:
Keep your elbows close to your body and avoid swinging.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Beginner", 1),

    ("Hammer curls", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Biceps and forearms

STARTING POSITION:
Hold a weight in each hand with your palms facing your thighs.

MOVEMENT:
Curl the weights upwards while keeping your palms facing inwards. Lower slowly.

IMPORTANT TIPS:
Keep your upper arms steady and avoid using momentum.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Beginner", 1),

    ("Tricep kickbacks", "Upper Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Triceps

STARTING POSITION:
Hold the weights and hinge forward slightly with your elbows bent close to your sides.

MOVEMENT:
Straighten your elbows to move the weights backwards, then return slowly.

IMPORTANT TIPS:
Keep your upper arms still and only move from the elbow.

BREATHING:
Breathe out as you extend, and breathe in as you return.
""", "Intermediate", 1),

    ("Goblet squat", "Lower Body",
"""EQUIPMENT REQUIRED:
Dumbbell or kettlebell

TARGET AREA:
Thighs, glutes, and core

STARTING POSITION:
Hold one weight close to your chest and stand with your feet shoulder-width apart.

MOVEMENT:
Lower into a squat, then return to standing.

IMPORTANT TIPS:
Keep your chest lifted and your knees aligned with your toes.

BREATHING:
Breathe in as you lower down, and breathe out as you stand up.
""", "Beginner", 1),

    ("Romanian deadlift", "Lower Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Hamstrings, glutes, and lower back

STARTING POSITION:
Stand upright holding the weights in front of your thighs.

MOVEMENT:
Hinge at the hips and lower the weights down your legs, then return to standing.

IMPORTANT TIPS:
Keep your back straight and slightly bend your knees. Do not round your spine.

BREATHING:
Breathe in as you lower, and breathe out as you stand up.
""", "Intermediate", 1),

    ("Walking lunges", "Lower Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Thighs, glutes, and balance

STARTING POSITION:
Stand upright holding weights by your sides.

MOVEMENT:
Step forward into a lunge, then bring the back leg through into the next lunge.

IMPORTANT TIPS:
Keep your upper body tall and your steps controlled.

BREATHING:
Breathe in as you lower into each lunge, and breathe out as you rise.
""", "Intermediate", 0),

    ("Sumo squats", "Lower Body",
"""EQUIPMENT REQUIRED:
Dumbbell or kettlebell

TARGET AREA:
Inner thighs, glutes, and hips

STARTING POSITION:
Stand with a wide stance and hold the weight in front of your body.

MOVEMENT:
Lower into a squat and return to standing.

IMPORTANT TIPS:
Keep your toes turned slightly outward and your knees tracking in the same direction.

BREATHING:
Breathe in as you lower, and breathe out as you rise.
""", "Beginner", 1),

    ("Russian twists (weighted)", "Core",
"""EQUIPMENT REQUIRED:
Dumbbell or kettlebell

TARGET AREA:
Core and obliques

STARTING POSITION:
Sit with your knees bent and hold the weight close to your chest.

MOVEMENT:
Lean back slightly and rotate your torso from side to side.

IMPORTANT TIPS:
Keep the movement controlled and avoid twisting too quickly.

BREATHING:
Breathe out as you twist to each side.
""", "Beginner", 1),

    ("Renegade rows", "Core",
"""EQUIPMENT REQUIRED:
Dumbbells

TARGET AREA:
Core, back, and arms

STARTING POSITION:
Start in a high plank position with your hands on the dumbbells.

MOVEMENT:
Pull one dumbbell towards your torso, lower it, then repeat on the other side.

IMPORTANT TIPS:
Keep your hips stable and avoid rotating your body too much.

BREATHING:
Breathe out as you row, and breathe in as you lower.
""", "Advanced", 0),

    ("Weighted sit-ups", "Core",
"""EQUIPMENT REQUIRED:
Dumbbell or kettlebell

TARGET AREA:
Core

STARTING POSITION:
Lie on your back holding the weight at your chest.

MOVEMENT:
Lift your upper body into a sit-up, then lower down slowly.

IMPORTANT TIPS:
Move with control and avoid jerking your neck forward.

BREATHING:
Breathe out as you sit up, and breathe in as you lower.
""", "Intermediate", 1),

    ("Farmer’s carry", "Full Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Grip, shoulders, core, and legs

STARTING POSITION:
Stand upright holding a weight in each hand by your sides.

MOVEMENT:
Walk forward slowly while keeping your body tall and stable.

IMPORTANT TIPS:
Keep your shoulders down and avoid leaning to one side.

BREATHING:
Breathe steadily as you walk.
""", "Intermediate", 0),

    ("Kettlebell swings", "Full Body",
"""EQUIPMENT REQUIRED:
Kettlebell

TARGET AREA:
Glutes, hamstrings, hips, and core

STARTING POSITION:
Stand with your feet slightly wider than hip-width apart and hold the kettlebell with both hands.

MOVEMENT:
Hinge at the hips to swing the kettlebell back, then drive your hips forward to swing it up.

IMPORTANT TIPS:
Use your hips to drive the movement, not your arms. Keep your back straight.

BREATHING:
Breathe out as you swing forward, and breathe in as it comes back down.
""", "Advanced", 0),

    ("Clean and press", "Full Body",
"""EQUIPMENT REQUIRED:
Dumbbell or kettlebell

TARGET AREA:
Full body, especially shoulders, arms, and legs

STARTING POSITION:
Stand upright holding the weight in front of your body.

MOVEMENT:
Lift the weight to shoulder level, then press it overhead. Lower it back down with control.

IMPORTANT TIPS:
Move smoothly and use a safe weight. Keep your core engaged.

BREATHING:
Breathe out as you lift and press, and breathe in as you lower.
""", "Advanced", 0),

    ("Thrusters", "Full Body",
"""EQUIPMENT REQUIRED:
Dumbbells or kettlebells

TARGET AREA:
Legs, shoulders, arms, and core

STARTING POSITION:
Hold the weights at shoulder height with your feet shoulder-width apart.

MOVEMENT:
Lower into a squat, then stand up and press the weights overhead in one smooth motion.

IMPORTANT TIPS:
Keep the movement controlled and avoid rushing between the squat and press.

BREATHING:
Breathe in as you lower, and breathe out as you stand and press.
""", "Advanced", 0),

    ("Turkish get-ups", "Full Body",
"""EQUIPMENT REQUIRED:
Dumbbell or kettlebell

TARGET AREA:
Full body, especially shoulders, core, and hips

STARTING POSITION:
Lie on your back holding one weight above you with one arm extended.

MOVEMENT:
Slowly move from lying down to standing while keeping the weight stable overhead, then reverse the movement.

IMPORTANT TIPS:
Perform this exercise slowly and only with proper control. Beginners should learn it in stages.

BREATHING:
Breathe steadily throughout the movement.
""", "Advanced", 0),

    # ==========================
    # MEDICINE BALL
    # ==========================

    ("Sit-ups with ball", "Core",
"""EQUIPMENT REQUIRED:
Medicine ball

TARGET AREA:
Core

STARTING POSITION:
Lie on your back holding the medicine ball at your chest.

MOVEMENT:
Lift your upper body into a sit-up, then lower down slowly.

IMPORTANT TIPS:
Keep the movement controlled and avoid using momentum.

BREATHING:
Breathe out as you sit up, and breathe in as you lower.
""", "Beginner", 1),

    ("Woodchoppers (medicine ball)", "Core",
"""EQUIPMENT REQUIRED:
Medicine ball

TARGET AREA:
Core, shoulders, and obliques

STARTING POSITION:
Stand or sit holding the medicine ball with both hands.

MOVEMENT:
Move the ball diagonally across your body in a controlled chopping motion, then return slowly.

IMPORTANT TIPS:
Rotate with control and keep your back tall.

BREATHING:
Breathe out as you move across, and breathe in as you return.
""", "Intermediate", 1),

    ("Push-ups on medicine ball", "Upper Body",
"""EQUIPMENT REQUIRED:
Medicine ball

TARGET AREA:
Chest, shoulders, arms, and core

STARTING POSITION:
Place one or both hands on the medicine ball in a push-up position.

MOVEMENT:
Lower your body towards the floor and push back up.

IMPORTANT TIPS:
This exercise is unstable and advanced. Use caution and move slowly.

BREATHING:
Breathe in as you lower, and breathe out as you push up.
""", "Advanced", 0),

    ("Squat to press", "Full Body",
"""EQUIPMENT REQUIRED:
Medicine ball

TARGET AREA:
Legs, shoulders, arms, and core

STARTING POSITION:
Hold the medicine ball at chest level with your feet shoulder-width apart.

MOVEMENT:
Lower into a squat, then stand up and press the ball overhead.

IMPORTANT TIPS:
Keep your chest lifted and move in one controlled motion.

BREATHING:
Breathe in as you lower, and breathe out as you stand and press.
""", "Intermediate", 0),

    ("Rotational throws", "Full Body",
"""EQUIPMENT REQUIRED:
Medicine ball and wall or partner

TARGET AREA:
Core, shoulders, and power development

STARTING POSITION:
Stand upright holding the medicine ball with both hands.

MOVEMENT:
Rotate your body and throw the ball to the side, then reset and repeat.

IMPORTANT TIPS:
Use a controlled twist and make sure you have enough space around you.

BREATHING:
Breathe out as you throw, and breathe in as you reset.
""", "Advanced", 0),

    ("Lunge with rotation", "Full Body",
"""EQUIPMENT REQUIRED:
Medicine ball

TARGET AREA:
Legs, core, and balance

STARTING POSITION:
Stand upright holding the medicine ball close to your chest.

MOVEMENT:
Step into a lunge and rotate your torso towards the front leg. Return to standing and repeat.

IMPORTANT TIPS:
Keep your front knee aligned with your foot and rotate with control.

BREATHING:
Breathe in as you lower into the lunge, and breathe out as you rotate and rise.
""", "Intermediate", 0),

    # ==========================
    # GYM EQUIPMENT
    # ==========================

    ("Pull-ups", "Upper Body",
"""EQUIPMENT REQUIRED:
Pull-up bar

TARGET AREA:
Back, shoulders, and arms

STARTING POSITION:
Hang from the pull-up bar with your hands placed slightly wider than shoulder-width apart.

MOVEMENT:
Pull your body upwards until your chin reaches the bar, then lower down slowly.

IMPORTANT TIPS:
Keep your movement controlled and avoid swinging.

BREATHING:
Breathe out as you pull up, and breathe in as you lower.
""", "Advanced", 0),

    ("Chin-ups", "Upper Body",
"""EQUIPMENT REQUIRED:
Pull-up bar

TARGET AREA:
Back, arms, and shoulders

STARTING POSITION:
Hang from the bar with your palms facing towards you.

MOVEMENT:
Pull yourself up until your chin is above the bar, then lower down slowly.

IMPORTANT TIPS:
Keep your body steady and avoid using momentum.

BREATHING:
Breathe out as you pull up, and breathe in as you lower.
""", "Advanced", 0),

    ("Hanging leg raises", "Core",
"""EQUIPMENT REQUIRED:
Pull-up bar

TARGET AREA:
Core and hip flexors

STARTING POSITION:
Hang from the pull-up bar with your arms extended.

MOVEMENT:
Lift your legs upwards as high as comfortable, then lower them slowly.

IMPORTANT TIPS:
Avoid swinging. Keep the movement controlled.

BREATHING:
Breathe out as you lift your legs, and breathe in as you lower.
""", "Advanced", 0),

    ("Dead hangs", "Upper Body",
"""EQUIPMENT REQUIRED:
Pull-up bar

TARGET AREA:
Grip, shoulders, and upper back

STARTING POSITION:
Hold onto the bar with both hands and let your body hang.

MOVEMENT:
Maintain the hanging position for the desired time.

IMPORTANT TIPS:
Keep your shoulders stable and avoid shrugging excessively.

BREATHING:
Breathe steadily throughout the hold.
""", "Beginner", 0),

    ("Smith machine squats", "Lower Body",
"""EQUIPMENT REQUIRED:
Smith machine

TARGET AREA:
Thighs, glutes, and hips

STARTING POSITION:
Stand under the bar with it resting across your upper back and your feet shoulder-width apart.

MOVEMENT:
Lower into a squat, then return to standing.

IMPORTANT TIPS:
Keep your chest up and your knees aligned with your toes.

BREATHING:
Breathe in as you lower, and breathe out as you stand.
""", "Beginner", 1),

    ("Incline press (smith)", "Upper Body",
"""EQUIPMENT REQUIRED:
Smith machine and incline bench

TARGET AREA:
Upper chest, shoulders, and arms

STARTING POSITION:
Lie on the incline bench under the bar and grip it slightly wider than shoulder-width apart.

MOVEMENT:
Lower the bar towards your upper chest, then press it back up.

IMPORTANT TIPS:
Move slowly and keep your wrists stable.

BREATHING:
Breathe in as you lower the bar, and breathe out as you press it up.
""", "Intermediate", 1),

    ("Hip thrusts (smith)", "Lower Body",
"""EQUIPMENT REQUIRED:
Smith machine and bench

TARGET AREA:
Glutes, hamstrings, and hips

STARTING POSITION:
Sit with your upper back against the bench and position the bar across your hips.

MOVEMENT:
Drive your hips upward until your body forms a straight line, then lower slowly.

IMPORTANT TIPS:
Keep your chin tucked slightly and squeeze your glutes at the top.

BREATHING:
Breathe out as you lift, and breathe in as you lower.
""", "Intermediate", 1),

    ("Lat pulldown", "Upper Body",
"""EQUIPMENT REQUIRED:
Lat pull down machine

TARGET AREA:
Back, shoulders, and arms

STARTING POSITION:
Sit at the machine and hold the bar with both hands.

MOVEMENT:
Pull the bar down towards your upper chest, then slowly return it upward.

IMPORTANT TIPS:
Keep your chest lifted and avoid leaning too far back.

BREATHING:
Breathe out as you pull down, and breathe in as you return.
""", "Beginner", 1),

    ("Seated rows", "Upper Body",
"""EQUIPMENT REQUIRED:
Row machine

TARGET AREA:
Back, shoulders, and arms

STARTING POSITION:
Sit at the row machine with your feet secured and your hands on the handles.

MOVEMENT:
Pull the handles towards your torso, then extend your arms slowly.

IMPORTANT TIPS:
Keep your back straight and squeeze your shoulder blades together.

BREATHING:
Breathe out as you row, and breathe in as you return.
""", "Beginner", 1),

    ("Abdominal bench sit-ups", "Core",
"""EQUIPMENT REQUIRED:
Abdominal bench

TARGET AREA:
Core

STARTING POSITION:
Lie back on the abdominal bench with your feet secured if needed.

MOVEMENT:
Lift your upper body into a sit-up, then lower down slowly.

IMPORTANT TIPS:
Avoid pulling your neck forward and keep the movement controlled.

BREATHING:
Breathe out as you sit up, and breathe in as you lower.
""", "Intermediate", 1),

    ("Leg press", "Lower Body",
"""EQUIPMENT REQUIRED:
Leg press machine

TARGET AREA:
Thighs, glutes, and calves

STARTING POSITION:
Sit on the machine with your feet flat on the platform.

MOVEMENT:
Push the platform away until your legs are nearly straight, then return slowly.

IMPORTANT TIPS:
Do not lock your knees. Keep your feet flat on the platform.

BREATHING:
Breathe out as you press, and breathe in as you return.
""", "Beginner", 1),

    ("Leg extension", "Lower Body",
"""EQUIPMENT REQUIRED:
Leg extension machine

TARGET AREA:
Quadriceps

STARTING POSITION:
Sit on the machine with your legs bent and the pad resting on your lower legs.

MOVEMENT:
Straighten your legs to lift the pad, then lower slowly.

IMPORTANT TIPS:
Do not swing the weight. Keep the movement smooth and controlled.

BREATHING:
Breathe out as you extend your legs, and breathe in as you lower.
""", "Beginner", 1),

    ("Seated Leg curl", "Lower Body",
"""EQUIPMENT REQUIRED:
Seated leg curl machine

TARGET AREA:
Hamstrings

STARTING POSITION:
Sit on the machine with your legs positioned against the pad.

MOVEMENT:
Bend your knees to pull the pad down or back, then return slowly.

IMPORTANT TIPS:
Keep your hips stable and avoid jerking the movement.

BREATHING:
Breathe out as you curl, and breathe in as you return.
""", "Beginner", 1),

    ("Lying Leg curl", "Lower Body",
"""EQUIPMENT REQUIRED:
Lying leg curl machine

TARGET AREA:
Hamstrings

STARTING POSITION:
Lie face down on the machine with the pad resting above your ankles.

MOVEMENT:
Bend your knees to lift the pad, then lower it slowly.

IMPORTANT TIPS:
Keep your hips on the bench and move with control.

BREATHING:
Breathe out as you curl, and breathe in as you lower.
""", "Beginner", 1),

    ("Hip abduction", "Lower Body",
"""EQUIPMENT REQUIRED:
Leg abduction machine

TARGET AREA:
Outer hips and glutes

STARTING POSITION:
Sit upright on the machine with your legs against the outer pads.

MOVEMENT:
Push your legs outward against the pads, then return slowly to the starting position.

IMPORTANT TIPS:
Keep your back supported and avoid using momentum.

BREATHING:
Breathe out as you push outward, and breathe in as you return.
""", "Beginner", 1),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for ex in EXERCISES:
        cur.execute("""
            INSERT OR IGNORE INTO Exercise
            (ExerciseName, TargetArea, Instructions, Difficulty, IsSeatedFriendly)
            VALUES (?, ?, ?, ?, ?)
        """, ex)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM Exercise")
    print("Total exercises in DB:", cur.fetchone()[0])

    conn.close()

if __name__ == "__main__":
    main()