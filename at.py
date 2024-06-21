import gym
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import cv2

# Hyperparameters
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_END = 0.01
EPSILON_DECAY = 0.995
BATCH_SIZE = 32
LEARNING_RATE = 0.00025
MEMORY_SIZE = 100000
TARGET_UPDATE_FREQ = 1000
EPISODES = 10000
START_LEARNING = 1000

# Preprocessing function
def preprocess_frame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    frame = cv2.resize(frame, (84, 84))
    frame = frame / 255.0
    return frame

# Define the Q-Network
class QNetwork(nn.Module):
    def __init__(self, input_shape, num_actions):
        super(QNetwork, self).__init__()
        self.conv1 = nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1)
        self.fc1 = nn.Linear(7 * 7 * 64, 512)
        self.fc2 = nn.Linear(512, num_actions)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Experience Replay Memory
class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def push(self, transition):
        self.memory.append(transition)

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

# Epsilon-greedy policy
def select_action(state, epsilon, q_network):
    if random.random() < epsilon:
        return env.action_space.sample()
    else:
        with torch.no_grad():
            state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
            q_values = q_network(state)
            return q_values.argmax().item()

# Training the Q-Network
def train_q_network(q_network, target_network, memory, optimizer):
    if len(memory) < BATCH_SIZE:
        return

    batch = memory.sample(BATCH_SIZE)
    states, actions, rewards, next_states, dones = zip(*batch)

    states = torch.tensor(states, dtype=torch.float32).to(device)
    actions = torch.tensor(actions, dtype=torch.int64).unsqueeze(1).to(device)
    rewards = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1).to(device)
    next_states = torch.tensor(next_states, dtype=torch.float32).to(device)
    dones = torch.tensor(dones, dtype=torch.float32).unsqueeze(1).to(device)

    current_q_values = q_network(states).gather(1, actions)
    next_q_values = target_network(next_states).max(1)[0].unsqueeze(1)
    target_q_values = rewards + (GAMMA * next_q_values * (1 - dones))

    loss = nn.MSELoss()(current_q_values, target_q_values)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# Main training loop
env = gym.make("ALE/Breakout-v5")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

q_network = QNetwork((1, 84, 84), env.action_space.n).to(device)
target_network = QNetwork((1, 84, 84), env.action_space.n).to(device)
target_network.load_state_dict(q_network.state_dict())
target_network.eval()

optimizer = optim.Adam(q_network.parameters(), lr=LEARNING_RATE)
memory = ReplayMemory(MEMORY_SIZE)
epsilon = EPSILON_START

for episode in range(EPISODES):
    state = preprocess_frame(env.reset())
    state = np.stack([state] * 4, axis=0)

    total_reward = 0
    done = False

    while not done:
        action = select_action(state, epsilon, q_network)
        next_frame, reward, done, _ = env.step(action)
        next_frame = preprocess_frame(next_frame)
        next_state = np.append(state[1:], np.expand_dims(next_frame, 0), axis=0)
        memory.push((state, action, reward, next_state, done))

        state = next_state
        total_reward += reward

        train_q_network(q_network, target_network, memory, optimizer)

        if episode % TARGET_UPDATE_FREQ == 0:
            target_network.load_state_dict(q_network.state_dict())

        epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

    print(f"Episode {episode} - Total Reward: {total_reward}, Epsilon: {epsilon}")

env.close()
