# MazeAI

I have been learning about Reinforcement Learning lately so I decided to put some of that knowlege to practice. Here, I created a tool to visually represent what is happening during the learning process of Q(λ). Users can observe how certain parameter affects the learning by watching the bot learn the maze or manually move the bot itself to see the results. 

Videos of the bot solving the mazes from start to finish:
- https://www.youtube.com/watch?v=sV-BAEK6WZo

![Image 1](https://media.giphy.com/media/l3mZft8CytWihcKk0/giphy.gif "Image 1")

# Screenshots

![Image 1](https://github.com/vinhvu200/MazeAI/raw/master/DemoImage/screenshots.png "Image 1")

# Overview

![Image 2](https://github.com/vinhvu200/MazeAI/raw/master/DemoImage/overview.png "Image 2")

- **Left Board**
  - This is the actual maze that the AI will be solving on
  - You will be able to watch it walk around the maze while updating the board on the right
- **Right Board**
  - This board shows all the termination squares with a point value assigned to them
    - Postive squares are ones you want to go to, while negatives are to be avoided
  - For the empty squares, these will show the moves AI will take when landing on it
  - There are circular indicators on each of these squares to show how "sure" it is of the move
- **Symbols**
  - **γ**: Discount value
  - **ε**: Epsilon-greedy policy
  - **α**: Learning rate
  - **λ**: Lambda (trace decay parameter)
- **Buttons**
  - **Learn**: toggle button for AI to start learning
    - When this is off, user may use 'W', 'A', 'S', 'D' to move
  - **Reset**: Restart the maze to the beginning before the AI has learned anything
  - **Speed**: toggle between speed 1, 2, or 3
  - **Maze**: toggle between maze 1, 2, or 3
  - **α** : Set the learning rate [0, 1]
  - **λ** : Set the lambda value [0, 1]
# Lambda Comparison
![Image 3](https://github.com/vinhvu200/MazeAI/raw/master/DemoImage/low_lambda.png "Image 3")
![Image 4](https://github.com/vinhvu200/MazeAI/raw/master/DemoImage/high_lambda.png "Image 4")

- Higher lambda gives more credit from a reward to more distant states
- Lambda = 1 is equivalent to Monte Carlo RL algorithm
- Compare the two images above and try running the two settings on Maze 1

# Challenge

![Image 5](https://github.com/vinhvu200/MazeAI/raw/master/DemoImage/challenge.png "Image 5")

With the settings above, the AI will often converge to +0.5 square instead of +1.0 square. Why does this happen and what setting should be changed to fix this? 

# Implementation

- Requires kivy 1.9.1
- Requires python 2.7
- This is a backward view implementation of Q(λ) using eligibility trace
- Arrows are only shown on the right board if it there exists only one Q-value bigger than the rest
- The move cost is 0.01
