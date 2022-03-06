from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

NPROD = 3
NCONS = 1
N = 5

def producer(empty_semaforos,nonempty_semaforos,storage, prodid):
    v = 0 
    for i in range(N): #reiteramos el proceso con cada productor N veces
        print (f"producer {current_process().name} produciendo")
        sleep(random.random()/3)
        empty_semaforos[prodid].acquire() #espero hasta que el storage del productor actual este vacio para producir
        v += random.randint(0,5) #el nuevo numero se genera sumando al anterior
        storage[prodid] = v #almacenamos en storage el nuevo número
        nonempty_semaforos[prodid].release() #indico que el storage del productor ya no esta vacio
        print (f"producer {current_process().name} almacenado {v}")
    empty_semaforos[prodid].acquire() #espero a que el consumidor consuma el ultimo producto
    storage[prodid] = -1 #cuando ha producido N veces añadimos -1 en su posición
    nonempty_semaforos[prodid].release() #indico que he producido el último, aunque sea un falso producto, para que el consumidor siga trabajando
    
def minimo(lista): #busca el minimo de una lista y su posicion a expeción de los -1
    minimo = max(lista)
    index=lista.index(minimo)
    for i in range(len(lista)):
        elem = lista[i]
        if elem<minimo and elem!=-1:
            minimo = elem
            index=i
    return minimo, index
    
def consumer(empty_semaforos,nonempty_semaforos, storage):  
    lista = []
    for i in range(NPROD):
        nonempty_semaforos[i].acquire() #wait, esperamos a que todos los productores hayan producido
    
    while list(storage) != ([-1]*NPROD):
        print ("consumer desalmacenando")
        sleep(random.random()/3)
        num, prodid = minimo(list(storage)) #tomamos el minimo, que es el siguiente que desalmacenamos
        lista.append(num)
        empty_semaforos[prodid].release() #indico que he vaciado el storage del productor cuyo numero era el minimo
        print (f"consumer consumiendo {num}")
        nonempty_semaforos[prodid].acquire() #espero a que el productor vuelva a llenarlo
    print ('Lista almacenada:', lista)

def main():
    storage = Array('i',NPROD)
    empty_semaforos=[]
    nonempty_semaforos=[]
    for i in range(NPROD):
        non_empty = Semaphore(0)
        empty = BoundedSemaphore(1)
        empty_semaforos.append(empty)
        nonempty_semaforos.append(non_empty)
    prodlst = [ Process(target = producer, 
                       name=f'prod_{i}', 
                       args=(empty_semaforos,nonempty_semaforos,storage,i))
                    for i in range (NPROD)]
    conslst = Process(target = consumer, args = (empty_semaforos,nonempty_semaforos,storage))
    
    for p in  prodlst + [conslst]:
        p.start()

    for p in prodlst + [conslst]:
        p.join()

if __name__ == "__main__":
    main()