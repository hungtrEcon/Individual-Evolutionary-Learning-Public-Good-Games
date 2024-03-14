###This script runs multiple simulations of IEL agents playing a Public Goods game with a voluntary contribution
###Mechanism and graphs the mean group contribution level

import random
from scipy.stats import truncnorm
import numpy as np
from sys import exit

import plotly
import plotly.graph_objs as go

rounds=10   # number of rounds per run
runs = 10  # number of runs in a simulation

su = 10  # upper bound on the strategy set [sl,su]
sl = 0  # lower bound on strategy set [sl,su]

I = 10  # number of subjects in a sim;
J = 10  # number of items in "considered set" S
muv = .033  # rate of mutation of value
w = su # tokens given to players every turn
sigmav = 1  # variance on the mutation of value
M =0.75 # marginal product of public good
beta_u = 22 #22 # upper bound on the range of beta
gamma_u = 8 # 8 upper bound on the range of gamma
P = 0.48 # probability of being selfish - beta and gamma are 0


def randominitialize(I, J, sl, su, P, beta_u, gamma_u):
    W = []
    St = []
    beta = []
    gamma = []

    ###Initialize the utility for each strategy W = [.., Wi, ..], Wi=[..,Wij,..]
    for i in range(I):
        temp = [1] * len(range(J))
        W.append(temp)

    ###Initialize the strategy set S = [.., St, ..], St = [.., Sit, ..], Sit = [..., sitj, .., sitJ]
    for i in range(I):
        Sit = []

        for j in range(J):
            Sit.append(random.uniform(sl, su))

        St.append(Sit)

        for i in range(I):
            if random.uniform(0,1) <= P:
                gamma.append(0)
                beta.append(0)
            else:
                gamma.append(random.uniform(0,gamma_u))
                beta.append(random.uniform(0,beta_u))

    return St, W , beta, gamma

def selectionfori(some_list, probabilities):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities): #this zip() return a pair of tuples where 1st element in each are paired and so on
        cumulative_probability += item_probability
        if x < cumulative_probability: break
    return item
# item is the selected strategy

def choiceprobabilitiesfori(utilities):
    choicepiti=[]
    e=min(utilities)
    if e <= 0:
        print("e<0")
        for j in range(J):
            utilities[j] -= e
    sumw=sum(utilities)
    if sumw == 0:
        exit("error - sumw=0")
    for j in range(J):
        choicepiti.append(utilities[j]/float(sumw))
    return choicepiti


def Vexperimentationfori(strategyset):
    # value experimentation - know sigmav,sl,su,muv, mul
    for j in range(J):
        if random.uniform(0, 1) < muv:
            centers = strategyset[j]
            r = (truncnorm.rvs((sl - centers) / float(sigmav),
                                (su - centers) / float(sigmav),
                                loc=centers, scale=sigmav, size=1))
            strategyset[j] = np.array(r).tolist()[0]
    return strategyset

def foregoneutility(strategy,past_actions,player_name,beta,gamma):
        #know L,t
        #print("strategy",strategy)
    temp_actions = list(past_actions)
    temp_actions[player_name]= strategy
        #print("temp_actions",temp_actions)
    profit =[]
    for i in range(I):

        profit.append(w-temp_actions[i]+M*sum(temp_actions))
        #print("profit",profit)
    utility = profit[player_name]+beta[player_name]*np.mean(profit)-gamma[player_name]*max(0,np.mean(profit)-profit[player_name])
        #print("utility",utility)
    return utility

def updateWfori(Set,past_actions,player_name,beta,gamma):
    W=[]

    for j in range(J):
        W.append(foregoneutility(Set[j],past_actions,player_name,beta,gamma))
        #W.append(10-Set[j])
    return W


def replicatefori(strategyset, utilities):
    newS = [0] * J
    newW = [0] * J
    for j in range(J):
        j1 = random.randrange(J)
        j2 = random.randrange(J)
        newS[j] = strategyset[j2]
        newW[j] = utilities[j2]
        if utilities[j1] > utilities[j2]:
            newS[j] = strategyset[j1]
            newW[j] = utilities[j1]
    return newS, newW


# this section is for the simulation parameters

#rounds=10   # number of rounds per run
#runs = 2  # number of runs in a simulation

# this is where the simulations start
a_mean_round_run = [[] for i in range(rounds)]  # stores the mean contribution by each round each run
# [[round1run1,round1run2,....][round2run1,round2run2...]....]
# initialize for a run (i.e. one play of repeated game)
a_mean_round= [0]*rounds # stores the mean contribution  of all rounds by each round
for sims in range(runs):

    random.seed()
    S = []  # stores strategy sets for each run
    a = []  # stores all actions for a run

    currentstrat = [0] * I

    [St, W,beta,gamma] = randominitialize(I, J, sl, su,P, beta_u,gamma_u)

    for t in range(rounds):
        # print "round = ",t
        # print ""
        at = []  # initializes actions for round t

        # this is the round play
        if t == 0: #if it is the first round, skip experiment, replicate.
            for i in range(I):
                p = choiceprobabilitiesfori(W[i])
                at.append(selectionfori(St[i], p))
            a_mean_round_run[t].append(np.mean(at))
            S.append(St)
            a.append(at)
        else:
            #print("at", a[len(a)-1])
            for i in range(I):

                St[i] = Vexperimentationfori(St[i])

                W[i] = updateWfori(St[i], a[len(a)-1], i,beta,gamma)
                (St[i], W[i]) = replicatefori(St[i], W[i])
                #print("i=",i, "act=",  "currentstrat =",currentstrat[i])
                #print("S=",  St[i])
                #print("W=",W[i])
            for i in range(I):
                p = choiceprobabilitiesfori(W[i])
                at.append(selectionfori(St[i], p))
            # this is record keeping of St and at


                #print("p",p)
            S.append(St)
            a.append(at)
            a_mean_round_run[t].append(np.mean(at))

    print("running", sims)


for t in range(rounds):
    a_mean_round[t]=np.mean(a_mean_round_run[t])


# Create traces
trace0 = go.Scatter(
    x = list(range(rounds)),
    y = list(a_mean_round),
    mode = 'lines+markers',
    name = 'lines'
)
layout = go.Layout(
    title='P=0.48,B=22,G=8,N='+str(I)+',M='+str(M),
    width=800,
    height=600,
    xaxis=dict(
        title='period',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='average contribution',
        nticks=10,
        range=[0,10],
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)
data = [trace0]
figure = go.Figure(data=data,layout=layout)
plotly.offline.plot(figure, filename='line-mode.html')
# (newS,newW) = (replicated strategies, corresponding foregone utilities)
print("average contribution per round",a_mean_round)

