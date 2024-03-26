# LLM to provide relations

Here is the log of our interactions with GPT-4 to obtain a set of relational functions, used by an RL agent playing pong:

##### Expert:
I am programming an RL agent to play Pong, where the goal is:
Knock the ball past the opponent's orange paddle on the left (good), and don't let it go past your green paddle on the right (bad).
There are 3 objects, the Player, Enemy and Paddle, that inherit from:
    
```python3
class GameObject:
    def __init__(self):
        self.rgb = (0, 0, 0)
        self._xy = (0, 0)
        self.wh = (0, 0)
        self._prev_xy = None
```

Can you give me a set of relational functions that the RL agent can apply on any two objects and that can be used within its policy ?

##### GPT-4:
For your Reinforcement Learning (RL) agent designed to play Pong, relational functions between game objects can significantly aid in crafting an effective policy. These functions should enable your agent to understand the relative positions and movements of the paddle and ball to make strategic decisions. Here are some relational functions that can be applied to any two objects, such as the player's paddle, enemy paddle, and the ball:

**Relative Position**: Determines the relative position of one object to another on both the X (horizontal) and Y (vertical) axes. This is crucial for understanding whether the ball is above, below, or on a direct path with the paddle.

**Distance Between Objects**: Calculates the Euclidean distance between two objects. This can be particularly useful for determining how far the ball is from the paddle, aiding in movement decisions to intercept or hit the ball.

**Approaching Angle**: Estimates the angle at which the ball is approaching the paddle. This can help in predicting where the ball will hit the paddle and in adjusting the paddle's position to control the ball's rebound direction.

**Relative Velocity**: Compares the velocity (speed and direction) of the ball relative to the paddle. This can inform the agent about the speed at which it needs to move the paddle to intercept or hit the ball effectively.

**Future Intersection Point**: Predicts the future intersection point of the ball with the paddle based on the current trajectory of the ball. This advanced calculation helps in positioning the paddle in the right place at the right time.

**Is Ball Approaching or Receding**: Determines whether the ball is moving towards or away from a given object, like the player's paddle. This can be crucial for deciding when to move the paddle for an interception or to prepare for the next shot.

**Predicted Time Until Intersection**: Estimates the time it will take for the ball to reach the paddle or cross the player's or enemy's goal line, based on its current trajectory and speed. This helps in timing the paddle's movements.

**Overlap Detection**: Checks if two objects are overlapping or if their bounding boxes intersect. This is particularly useful for collision detection between the ball and the paddle.

Implementing these functions will require access to the properties of each GameObject, such as their positions (`_xy`), dimensions (`wh`), and possibly their previous positions (`_prev_xy`) to calculate velocities and trajectories. By integrating these relational functions into your RL agent's policy, you can enhance its ability to make strategic decisions based on the dynamic states of the game objects involved in Pong.

##### Expert:
Can you give me the code for each of these functions ?

##### GPT-4:

Certainly! Below are Python functions that implement the relational concepts for objects in your Pong game. These assume that each object (player paddle, enemy paddle, ball) is an instance of GameObject or a subclass with the necessary properties.

First, ensure your GameObject class has all the necessary attributes. You mentioned a simplified version; let's expand it a bit for our purposes:

```python3
class GameObject:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.rgb = (0, 0, 0)
        self._xy = (x, y)
        self.wh = (w, h)
        self._prev_xy = (x, y)
```

Now, let's define the relational functions:

```python3
import math

def relative_position(object1, object2):
    """Returns the relative position of object1 to object2."""
    return object2._xy[0] - object1._xy[0], object2._xy[1] - object1._xy[1]

def distance_between_objects(object1, object2):
    """Calculates the Euclidean distance between two objects."""
    return math.sqrt((object2._xy[0] - object1._xy[0])**2 + (object2._xy[1] - object1._xy[1])**2)

def approaching_angle(object1, object2):
    """Estimates the angle at which object1 is approaching object2."""
    dx, dy = relative_position(object1, object2)
    return math.atan2(dy, dx)

def relative_velocity(object1, object2):
    """Compares the velocity of object1 relative to object2."""
    dx1 = object1._xy[0] - object1._prev_xy[0]
    dy1 = object1._xy[1] - object1._prev_xy[1]
    dx2 = object2._xy[0] - object2._prev_xy[0]
    dy2 = object2._xy[1] - object2._prev_xy[1]
    return dx1 - dx2, dy1 - dy2

def future_intersection_point(object1, object2, object1_velocity):
    """Predicts future intersection point of object1 with object2 based on object1's velocity."""
    # This is a simplified version assuming straight-line motion
    # and doesn't account for changes in direction or speed.
    dx, dy = object1_velocity
    time_to_intersection = (object2._xy[0] - object1._xy[0]) / dx if dx != 0 else float('inf')
    predicted_y_intersection = object1._xy[1] + dy * time_to_intersection
    return object2._xy[0], predicted_y_intersection

def is_ball_approaching_or_receding(ball, paddle):
    """Determines if the ball is moving towards or away from the paddle."""
    dx, _ = relative_velocity(ball, paddle)
    return "Approaching" if dx < 0 else "Receding"

def predicted_time_until_intersection(object1, object2, object1_velocity):
    """Estimates time until object1 intersects with object2 based on current trajectory."""
    dx, _ = object1_velocity
    return (object2._xy[0] - object1._xy[0]) / dx if dx != 0 else float('inf')

def overlap_detection(object1, object2):
    """Checks if object1 and object2 are overlapping."""
    x1_min, y1_min = object1._xy
    x2_min, y2_min = object2._xy
    x1_max, y1_max = x1_min + object1.wh[0], y1_min + object1.wh[1]
    x2_max, y2_max = x2_min + object2.wh[0], y2_min + object2.wh[1]
    return not (x1_max < x2_min or x2_max < x1_min or y1_max < y2_min or y2_max < y1_min)
```

These functions are starting points and might need adjustments based on your specific game mechanics, object properties, and how you've implemented motion in your game. For instance, the function for predicting the future intersection point assumes linear motion and doesn't account for the possibility of the ball changing direction upon hitting walls or paddles. You'll also want to fine-tune them based on the scale of your game's coordinates and velocity measurements.