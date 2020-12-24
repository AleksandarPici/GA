import math
import matplotlib
import matplotlib.pyplot as plt
import random
import pdb

# vraca random parove (ugao, brzina) ugao vraca izmedju 0-180 a brizinu uzima iz opsega 2-20 brzina mora da bude veca od nule 
def random_tries(items):                                                          #1. za pocetak treba kreirati random parove sa brzinom vecom od nule
  return [(random.uniform(0.1, math.pi), random.uniform(2, 20))                   # i uglom vecim od nula stepeni i manjim od pi u suprotnom ce ispaljivati u zemlju
		  for _ in range(items)]                                                 

def hit_coordinate(theta, v, width):                                              #3. Ljudsko oko posmatrajuci lik kretanja kugle moze odlciti koje resenje je bolje.
  x = 0.5 * width                                                                 # Kako masina da donese takvu odluku? PP da se kugla nalazi na sredini. Sirina je 10 unita npr. racunamo 0.5*10=5 unita levo ili desno dolazi do ivice kese
  x_hit = width                                                                   # dakle, x koliko unita od koordinatnog pocetka treba kugla da napravi do ivice kese a x_hit predstavlja granicu (ivicu kese)
  if theta > math.pi/2:                                                           # da li ide ulevo ili udesno kugla u odnosu na koordinatni pocetak
    x = -x                                                                        # ukoliko ide ulevo onda granica X ima negativnu vrednost
    x_hit = 0                                                                     # tada je takodje i leva granica kese u koordinatnom pocetku
  t = x / (v * math.cos(theta))                                                   #vreme potrebno da dodje do ivice kese jer nam je poznata brzina v i ugao teta
  y = v * t * math.sin(theta) - 0.5 * 9.81 * t * t                                #kada smo nasli t moguce je izracunati visinu y koju dostize u visini kese
  if y < 0 : y=0.0
  return x_hit, y                                                                 # dakle po x osi kugla moze da se dodje do leve ivice -5 ili +5 do desne ivice a y koordinata se preracunava formulom                                                               

def escaped(theta, v, width, height):                                             #4. definise se uslov za izlzac iz kese
  x_hit, y_hit = hit_coordinate(theta, v, width)
  return (x_hit==0 or x_hit==width) and y_hit > height                            # ukoliko je X - dosla do granice kese ulevo ili udesno i y-visina prelazi visinu kese

#trigonometrijaza kuglu i neko vreme t
#               x=v*t*cos(ugao)
#               Y=v*t*sin(ugao)-1/2*g*t*t
# t-vreme
# g-zemljina teza ~9.81
def launch(generation, height, width):                                            #11. pokrece funkciju lanziranja kugle za svaku generaciju
  results = []
  for (theta, v) in generation:                                                   # za svaki par (ugao,brizina) ispaljivanja kugle
    x_hit, y_hit = hit_coordinate(theta, v, width)                                # vrsi se izracunavanje predjenog puta
    good = escaped(theta, v, width, height)                                       # provera da li je kugla napustila kesu
    result = []
    result.append((width/2.0, 0.0))                                               # rezultat pocinje da generise iz koordinatnog pocetka
    for i in range(1, 20):                                                        # do 20 jer je tolika sirina grafikona                                              
      t = i * 0.2                                                                 # vreme ide od 0.2 do 4
      x = width/2.0 + v * t * math.cos(theta)                                     # width/2 oznacava koordinatni pocetak
      y = v * t * math.sin(theta) - 0.5 * 9.81 * t * t
      if y < 0: y = 0
      if not good and not(0 < x < width):                                         # ukoliko nije van granica kese i sledeci x nije unutar kese
        result.append((x_hit, y_hit))
        break                                                                     # staje
      result.append((x, y))
    results.append(result)                                                        # smesta rezultate ispaljivanja
  return results

def cumulative_probabilities(results):                                                          #5. sabira svaku vrednost iz rezultata i formira listu rezulta
  cp = []
  total = 0
  for res in results:
    total += res
    cp.append(total)                                                                            # sto je veca vrednost te bolja
  return cp 
  
#u result se smestaju smao y koordinate za prosledjjenu generaciju
# pa se zatim te vrednosti sabiraju i pravi se lista tih vrednosti
def selection(generation, width):                                                               #2. GA bira jake i bilje roditelje kako bi preneo bolje gene deci.
  results = [hit_coordinate(theta, v, width)[1] for (theta, v) in generation]                   # za prosledjenu generaciju vrati rezultate ispaljivanja kugli koordinate
  return cumulative_probabilities(results)                                                      # sabira vrednosti i vraca ih nazad kao listu 

# tocak za rulet
def choose(choices):                                                                            #7. izbor boljeg roditelja
  p = random.uniform(0, choices[-1])                                                            # izaberi random broj u opsegu od 0-poslednjeg broja koji se nalazi u listi choices
  for i in range(len(choices)):                                                                 # za svaki broj u listi choices
    if choices[i] >= p:                                                                         # ukoliko je bar jedan >=P vrati index tog broja
      return i

def breed(mum, dad):                                                                            #8. kreiranje deteta kombinovanjem prve polovene prvog roditelja i druge polovine drugog roditelja
  return (mum[0], dad[1])

def crossover(generation, width):                                                               #6. Kako imamo populaciju potrebno je izabratu sada bolje roditelje.
  choices = selection(generation, width)                                                        #izaberi iz generacije roditelje i kreiraj novu generaciju
  next_generation = []
  for i in range(0, len(generation)):
    mum = generation[choose(choices)]                                                           #izaberi prvog roditelja tako sto iz generacije vrati vrednost koja zadovoljava uslov da je >=p
    dad = generation[choose(choices)]                                                           # isto to uradi i za drugog roditelja
    next_generation.append(breed(mum, dad))                                                     #poziva breed za kreiranje deteta tako sto kombinuje roditelje (ugao uzima od jednog roditelja a brzinu od drugog)
  return next_generation                                                                        #vraca novu generaciju

def mutate(generation):                                                                         #9. da bi napravili malu razliku u odnosu na gene roditelja primenjujemo mutaciju
                                                                                                # kao i u evoluciji mutacija pomaze prilikom prirodne selekcije gde novi, jaci i bolji opstaju
  for i in range(len(generation)-1):
    (theta, v) = generation[i]
    if random.random() < 0.1:                                                                   #probablistic mutation ukoliko bi svaki put radili mutaciju onda bi to bila deterministic
      new_theta = theta + random.uniform(-10, 10) * math.pi/180                                 # uvecava se ugao teta i smesta se u new_theta - vrednost je u radijanima pi/180
      if 0 < new_theta < 2*math.pi:                                                             # samo ukoliko je novi ugao izmedju 0-180 stepeni
        theta = new_theta                                                                       # vrsi se zamena uglova trenutni ugao postaje novi
    if random.random() < 0.1:
      v *= random.uniform(0.9, 1.1)                                                             #brzinu ovecavamo za male intervale izmenju 0.9 i 1.1
    generation[i] = (theta, v)
    
def display(generation, ax, height, width):                                         #10. crta velicinu kese 
  rect = plt.Rectangle((0, 0), width, height, facecolor='gray')                     # crta pravougaonik sa donjim levim uglom u 0,0, i wisinom i sirinom
  ax.add_patch(rect)
  ax.set_xlabel('x')                                                                # oznaci X osu
  ax.set_ylabel('y')                                                                # oznaci Y osu
  ax.set_xlim(-width, 2 * width)                                                    # ostavlja mali prostor van kese sa leve i desne strane koliko je siroka kesa
  ax.set_ylim(0, 4.0 * height)                                                      # visina prostora je visina kese pomnozena sa 4
  free = 0
  result = launch(generation, height, width)                                        # za prosledjenu generaciju parova ispali kugle i vrati koordinate
  for res, (theta, v) in zip(result, generation):                                   # za svaki par dobijenih rezultata za prosledjenu generaciju
    x = [j[0] for j in res]
    y = [j[1] for j in res]
    if escaped(theta, v, width, height):                                            #poziva se funkcija koja kaze da li je kugla napustila kesu
      ax.plot(x, y, 'ro-', linewidth=2.0)                                           #ukoliko jeste koriste se r0 -crveni krugovi i linije za iscrtavanje putanje-luka
      free += 1
    else:
      ax.plot(x, y, 'bx-', linewidth=2.0)                                           # u suprotnom se iscrtava plavom bojom bx
  print ("Escaped", free)                                                           # stampa broj ispaljenih kugli van kese

def display_start_and_finish(generation0, generation, height, width):
  matplotlib.rcParams.update({'font.size': 18})
  fig = plt.figure()
  ax0 = fig.add_subplot(2,1,1)                                                       #2 plots in one column; first plot 
  ax0.set_title('Initial attempt')
  display(generation0, ax0, height, width)
  ax = fig.add_subplot(2,1,2)                                                        #second plot
  ax.set_title('Final attempt')
  display(generation, ax, height, width)
  plt.show()

def fire():                                                                           #10. pokretanje           
  epochs = 10                                 # koliko puta se primenjuje ukrstalje i mutacija   10*12 ispaljivanje kugle
  items = 12                                  # po 12 ispaljivanja kugli - koordinata
  height = 5                                  # visina kese
  width = 10                                  # sirina kese

  generation = random_tries(items)
  generation0 = list(generation)              # save to contrast with last epoch

  for i in range(1, epochs):                  #za svaku generaciju
    results = []
    generation = crossover(generation, width) # svaku generaciju ukrsti
    mutate(generation)                        #i primeni mutaciju

  display_start_and_finish(generation0, generation, height, width)

def single_shot():
  height = 5
  width = 10
  generation = [(math.pi/3, 8), (math.pi/4, 15), (math.pi/3, 15), (math.pi/3, 5)]   # staticki definise koordinate kako bi se objasnio problem i definisao zadatak
  matplotlib.rcParams.update({'font.size': 18})
  ax = plt.axes()                                                                   
  ax.set_title('Cannon balls fired once')
  display(generation, ax, height, width)
  plt.show()

if __name__ == "__main__":
  # single_shot()
  # pdb.set_trace()
  fire()