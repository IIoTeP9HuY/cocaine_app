#!/usr/bin/env python

def prepareModel():
  '''Reading data'''
  data = open('brown_bigrams_tagged.txt', 'r')
  inputLines = data.readlines()

  # lines = [line.rstrip().split('\t') for line in inputLines]
  lines = [[s.lower() for s in line.rstrip('\n').split('\t')] for line in inputLines]

  '''Filling frequences info'''
  tagPairFrequency = dict()
  wordTagFrequency = dict()
  wordFrequency = dict()
  tagFrequency = dict()
  tagPairProbability = dict()
  wordTagProbability = dict()
  tags = set()
  for line in lines:
      tag1 = line[1]
      tag2 = line[3]
      word1 = line[0]
      word2 = line[2]
      tags.add(tag1)
      tags.add(tag2)
      frequency = int(line[4])
      tagBigram = tag1 + ' ' + tag2
      wordTagBigram1 = word1 + ' ' + tag1
      wordTagBigram2 = word2 + ' ' + tag2
      tagFrequency[tag1] = tagFrequency.get(tag1, 0) + frequency
      wordFrequency[word1] = wordFrequency.get(word1, 0) + frequency
      tagPairFrequency[tagBigram] = tagPairFrequency.get(tagBigram, 0) + frequency
      wordTagFrequency[wordTagBigram1] = wordTagFrequency.get(wordTagBigram1, 0) + frequency

  V = len(tagFrequency)
  tags = list(tags)

  '''Filling probabilities info'''
  for key in tagPairFrequency.keys():
      tagPairProbability[key] = float(tagPairFrequency.get(key, 0)) / (tagFrequency.get(key.split()[0], 0))
      
  for key in wordTagFrequency.keys():
      wordTagProbability[key] = float(wordTagFrequency[key] + 1) / (tagFrequency[key.split()[1]] + V)

  return {"tagPair": tagPairProbability, "wordTag": wordTagProbability, "tags": tags}

# log = Logger()

'''Viterbi algorithm'''
def viterbi(O, tagPairProbability, wordTagProbability, tags):
  # log.debug('Tags: \'{0}\''.format(str(tags)))
  statesNumber = len(tags)
  stepsNumber = len(O) + 1
  stateProbability = []
  for i in range(0, statesNumber):
    stateProbability.append([0.0] * stepsNumber)

  # stateProbability = np.zeros((statesNumber, stepsNumber), dtype=np.float32)
  backtrack = []
  for i in range(0, statesNumber):
    backtrack.append([0] * stepsNumber)
  # backtrack = np.zeros((statesNumber, stepsNumber), dtype=np.int32)
  for i in range(0, statesNumber):
    stateProbability[i][0] = 1.0 / statesNumber

  # stateProbability[:, 0] = 1.0 / statesNumber
  for step in range(1, stepsNumber):
      word = O[step - 1]
      for currentState in range(0, statesNumber):
          currentTag = tags[currentState]
          wordTagPair = word + ' ' + currentTag
          currentWordTagProbability = wordTagProbability.get(wordTagPair, 0)
          for previousState in range(0, statesNumber):
              if currentState == previousState:
                  continue
              
              previousTag = tags[previousState]
              tagPair = previousTag + ' ' + currentTag
              currentTagPairProbability = tagPairProbability.get(tagPair, 0)
              previousProbability = stateProbability[previousState][step - 1]
              probability = previousProbability * currentTagPairProbability * currentWordTagProbability
              if stateProbability[currentState][step] < probability:
                  stateProbability[currentState][step] = probability
                  backtrack[currentState][step] = previousState
  
  mostProbableState = 0
  mostProbableStateProbability = stateProbability[0][stepsNumber - 1]
  for currentState in range(0, statesNumber):
      if stateProbability[currentState][stepsNumber - 1] > mostProbableStateProbability:
          mostProbableStateProbability = stateProbability[currentState][stepsNumber - 1]
          mostProbableState = currentState
  
  states = [0] * (stepsNumber - 1)
  # states = np.zeros(stepsNumber - 1, dtype=np.int32)
  currentState = mostProbableState
  for step in reversed(range(1, stepsNumber)):
      states[step - 1] = currentState
      currentState = backtrack[currentState][step]
      
  return [tags[s] for s in states]
  # print(mostProbableStateProbability)
  # print([tags[s] for s in states])
  

def posTagPhrase(phrase):
    return viterbi(phrase.split(), tagPairProbability, wordTagProbability, tags)

def test():
    model = prepareModel()
    message = "i love birds"
    tagging = viterbi(message.split(), model["tagPair"], model["wordTag"], model["tags"]);
    print(tagging)


import msgpack
from cocaine.decorators import http

from cocaine.worker import Worker
from cocaine.logging import Logger

@http
def main(request, response):
    # response.write_head(200, [("Content-Type", "plain/text")])
    response.write_head(200, [("Content-Type", "text/html")])

    request = yield request.read()
    message = request.request.get('message', None)

    tagging = []
    if (message == None):
      message = ""
    else:
      model = prepareModel()
      tagging = viterbi(message.split(), model["tagPair"], model["wordTag"], model["tags"]);

    html = """
      <html>
      <body>

      <h1>Part of the speech tagging!</h1>
    """

    if len(tagging) > 0:
      html += """
        <h2>%s  --->  %s</h2>
      """ % (str(message.split()), str(tagging))

    html += """
      <form name="submitform" method="get" onSubmit="window.location.replace('/?message=' + document.submitform['sentence'])">
        Sentence: <input type="text" name="message"><br>
        <input type="submit" value="Submit">
      </form>
    """

    html += """
      Please, send your suggestions to: kashin.andrej@gmail.com
      </body>
      </html>
    """
    # message = "i love birds"

    # response.write(str(message) + " " + str(tagging))
    response.write(html)
    response.close()


W = Worker()
W.run({
    'posTag': main,
})

# test()
