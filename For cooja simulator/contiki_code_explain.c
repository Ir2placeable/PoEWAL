#include "contiki.h"
#include "lib/list.h"
#include "lib/memb.h"
#include "lib/random.h"
#include "net/rime/rime.h"
#include "sys/rtimer.h"
#include "random.h"

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stddef.h>

#define MYPERFORM = 100;//Sets the performance of the node running the current code to a random value

#define MALLOC(p,s) \
    if (!(p = malloc(s))){\
        fprintf(stderr, "MALLOC Insufficient memory");\
            exit(EXIT_FAILURE);\
    }

#define REALLOC(p,s) \
    if (!(p = realloc(p,s))) { \
        fprintf(stderr, "REALLOC Insufficient memory");\
            exit(EXIT_FAILURE);\
    }

/*Below is a transaction structure that is the basic element of a block.
Defines the collected information of nodes in IoT healthcare.
*/
typedef struct transaction 
{
    int pulse;
    int oxygen;
    int temp;
}Transaction;
/*current_transactions is the struct array to collect the sensor datas
for make a block.*/
Transaction current_transactions[100];
int lastOfctran = -1; //lastOfctran is the index of current_transactions array.


int new_transaction(int pulse, int oxygen, int temp){
    if(lastOfctran>99)
    {
        printf("Too many transactions! this transaction will be ignored.");
        return -1;
        }
    else{
        
        current_transactions[++lastOfctran].pulse = pulse;
        current_transactions[lastOfctran].oxygen = oxygen;
        current_transactions[lastOfctran].temp = temp;
        
        printf("Current transaction in this noed:\n{\"transaction\": [\n");
        
        int i=0;
        while(i<lastOfctran){ //print current transaction
                printf("\t\t {\n");
                printf("\t\t\t\"pulse\": %d\n", current_transactions[i].pulse);
                printf("\t\t\t\"oxygen\": %d\n", current_transactions[i].oxygen);
                printf("\t\t\t\"temp\": %d\n",current_transactions[i].temp);
                printf("\t\t },\n");
                i++;
            }
        printf("\t\t]\n");
        printf("}");
    
    }
   return 1;
}

typedef struct results{//Structure to return values (proof and difficulty) of Pow result.
    int proof;
    int difficulty;
}PoWEresult;

typedef struct block // Implement a block dictionary in Python code as a structure.
{
    int index;
    long long int timestamp;
    Transaction transactions[100];//check
    int proof;
    char previous_hash[1024];
}Block;

Block myblock;// Block to do proof-of-work before being added to the shared ledger.
typedef struct chain{ //Block [2048]
    Block block;
}Blockchain;

/*Implemented as a dynamic array like vector in C++*/

Blockchain *chain; //"Local" shared ledger
int chainSize =1;
int lastOfchain = -1;//chain length == lastOfchain+1
Block last_block(){
    return chain[last_block];
}
void push_back_c(Block ablock){// Used to add a block to the chain
    if(lastOfVector >= chainSize-1) chainFull();//when there is no free space.
    chain[++lastOfVector] = ablock;
}
void chainFull_c(){
    REALLOC(chain, 2*chainSize*sizeof(*chain));
    chainSize*=2;
    printf("chain chain is extended!!\n");
}
void init_chain()
{
    //Initial vector size is 1 vector to store blocks
    MALLOC(chain, chainSize*sizeof(*chain));
    new_block(1, 100);//genesis block
}
Block new_block(char* previous_hash, int proof) //check
{  
    Block b;
    b.index = lastOfVector+1;
    b.timestamp = time(NULL);
    b.transactions[++lastOfctran] = current_transactions;
    b.proof = proof;
    b.previous_hash = previous_hash;

    current_transactions={ 0, };
    lastOfctran=-1;
    push_back_c(b);
    return b;
}
Block new_block2(int proof) //Works like a 'constructor' with the above function
{ 
    Block b;
    b.index = lastOfVector+1;
    b.timestamp = time(NULL);
    b.transactions->oxygen = current_transaction[].oxygen;
    b.proof = proof;
    b.previous_hash = hash(chain[-1]);//check

    current_transactions={ 0, };
    lastOfctran = -1;
    push_back_c(b);
    return b;
}

static struct unicast_conn uc;
//this is a message form to send and recieve unicast / broadcast / multicast
typedef struct msg {char * msg; int num;}Msg;

static void
recv_uc(struct unicast_conn *c, const linkaddr_t *from)
{
        Msg* msg;
        msg = packetbuf_dataptr();
  printf("unicast message received from %d.%d\n%s\n",
         from->u8[0], from->u8[1], msg->msg);

if(msg->msg[0]== "L")//Let's mine
        {
        msg->msg = "ok";        
        packetbuf_copyfrom(msg, sizeof(Msg));
        unicast_send(&c, &from);
        }
unicast_close(&c);
}
/*---------------------------------------------------------------------------*/
static void
sent_uc(struct unicast_conn *c, int status, int num_tx)
{
  const linkaddr_t *dest = packetbuf_addr(PACKETBUF_ADDR_RECEIVER);
  if(linkaddr_cmp(dest, &linkaddr_null)) {
    return;
  }
  printf("unicast message sent to %d.%d: status %d num_tx %d\n",
    dest->u8[0], dest->u8[1], status, num_tx);
}
static const struct unicast_callbacks unicast_callbacks = {recv_uc, sent_uc};


/*----neighbor------
Originally, we wanted to select a winner through a gossip algorithm
through a list of neighboring nodes.*/

struct broadcast_message {
  uint8_t seqno;
};

struct unicast_message {
  uint8_t type; //rime node address.
  char * msms;//The part that stores the value to be sent as unicast.
};

enum {
  UNICAST_TYPE_PING,
  UNICAST_TYPE_PONG
};

struct neighbor{// it is from contiki reference. example-rime-neighbor
  struct neighbor *next;
  linkaddr_t addr;

  uint16_t last_rssi, last_lqi;
  uint8_t last_seqno;
  uint32_t avg_seqno_gap;
  //this value will save neighbor node's PoW result.
  PoWEresult result = {0, 9999};
}

#define MAX_NEIGHBORS 16
MEMB(neighbors_memb, struct neighbor, MAX_NEIGHBORS);
LIST(neighbors_list);
static struct broadcast_conn broadcast;
static struct broadcast_conn broadcast2;//to deal with command of head node
static struct unicast_conn unicast;
#define SEQNO_EWMA_UNITY 0x100
#define SEQNO_EWMA_ALPHA 0x040

/*not complete
Trying to select a winner by reading the list of neighbors
and voting for the node that is the winner;broadcast
then if a node get recieve vote that more than 1/2list_length
the node will be winner and be able to start making a block.
*/
struct neighbor Find_winner(){
    int max =0;
    int collected_diff[15];
    int nonce_of_max;
    struct neighbor *p ,*w = list_head(neighbors_list);
    for(int i =0; i<list_length(neighbors_list); i++){
      if(max < p->difficulty) {max = p->difficulty;
                                nonce_of_max= p->nonce;
                                w = p;}
      else if (max==p->difficulty){
          if(nonce_of_max > p->nonce){w = p;}
        }
      p = list_item_next(p);
    }
    return w;
}
static void
broadcast_recv(struct broadcast_conn *c, const linkaddr_t *from)
{
  struct neighbor *n;
  struct broadcast_message *m;
  uint8_t seqno_gap;

  /* The packetbuf_dataptr() returns a pointer to the first data byte
     in the received packet. */
  m = packetbuf_dataptr();

  /* Check if we already know this neighbor. */
  for(n = list_head(neighbors_list); n != NULL; n = list_item_next(n)) {

    /* We break out of the loop if the address of the neighbor matches
       the address of the neighbor from which we received this
       broadcast message. */
    if(linkaddr_cmp(&n->addr, from)) {
      break;
    }
  }

  /* If n is NULL, this neighbor was not found in our list, and we
     allocate a new struct neighbor from the neighbors_memb memory
     pool. */
  if(n == NULL) {
    n = memb_alloc(&neighbors_memb);

    /* If we could not allocate a new neighbor entry, we give up. We
       could have reused an old neighbor entry, but we do not do this
       for now. */
    if(n == NULL) {
      return;
    }

    /* Initialize the fields. */
    linkaddr_copy(&n->addr, from);
    n->last_seqno = m->seqno - 1;
    n->avg_seqno_gap = SEQNO_EWMA_UNITY;

    /* Place the neighbor on the neighbor list. */
    list_add(neighbors_list, n);
  }

  /* We can now fill in the fields in our neighbor entry. */
  n->last_rssi = packetbuf_attr(PACKETBUF_ATTR_RSSI);
  n->last_lqi = packetbuf_attr(PACKETBUF_ATTR_LINK_QUALITY);

  /* Compute the average sequence number gap we have seen from this neighbor. */
  seqno_gap = m->seqno - n->last_seqno;
  n->avg_seqno_gap = (((uint32_t)seqno_gap * SEQNO_EWMA_UNITY) *
                      SEQNO_EWMA_ALPHA) / SEQNO_EWMA_UNITY +
                      ((uint32_t)n->avg_seqno_gap * (SEQNO_EWMA_UNITY -
                                                     SEQNO_EWMA_ALPHA)) /
    SEQNO_EWMA_UNITY;

  /* Remember last seqno we heard. */
  n->last_seqno = m->seqno;

  /* Print out a message. */
  printf("broadcast message received from %d.%d with seqno %d, RSSI %u, LQI %u, avg seqno gap %d.%02d\n",
         from->u8[0], from->u8[1],
         m->seqno,
         packetbuf_attr(PACKETBUF_ATTR_RSSI),
         packetbuf_attr(PACKETBUF_ATTR_LINK_QUALITY),
         (int)(n->avg_seqno_gap / SEQNO_EWMA_UNITY),
         (int)(((100UL * n->avg_seqno_gap) / SEQNO_EWMA_UNITY) % 100));
}
static const struct broadcast_callbacks broadcast_call = {broadcast_recv};

//command broadcast
static void
command_recv(struct broadcast_conn *c, const linkaddr_t *from)
{
    Msg* msg;
    msg = packetbuf_dataptr();

    if(msg->msg[0] == 'L') //Let's mining
    {
    msg->msg = "Timeframe plz"
    unicast_open(&uc, 146, &unicast_callbacks);      
    packetbuf_copyfrom(msg, sizeof(Msg));
    addr.u8[0] = 1;//head addr
    addr.u8[1] = 0;
    unicast_send(&uc, &addr);
}




PROCESS(broadcast_process, "By throug Broadcast, each nodes inform their existence
and add neighbor nodes to the neighbor list.");
//PROCESS(unicast_process, "unicast");
PROCESS(make_sensed_data_process, "Create a transaction variable at random times");
PROCESS(main_process, "A part to put to be executed sequentially;may not need");
AUTOSTART_PROCESSES(&main_process,&make_sensed_data_process,&broadcast_process);



/*---------------------------------------------------------------------------*/
PROCESS_THREAD(main_process, ev, data)
{
  PROCESS_BEGIN();
    //init block
    MALLOC(chain, chainSize*sizeof(*chain));
    new_block(1, 100);//genesis block into chain
  

  while (1)
  {
    //resolve_conflicts()
  }
  
  
  PROCESS_END();
}

PROCESS_THREAD(broadcast_process, ev, data)
{
  static struct etimer et;
  static uint8_t seqno;
  struct broadcast_message msg;

  PROCESS_EXITHANDLER(broadcast_close(&broadcast);)

  PROCESS_BEGIN();

  broadcast_open(&broadcast, 129, &broadcast_call);

  while(1) {

    /* Send a broadcast every 16 - 32 seconds*/
    etimer_set(&et, CLOCK_SECOND * 16 + random_rand() % (CLOCK_SECOND * 16));

    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    msg.seqno = seqno;
  
    packetbuf_copyfrom(&msg, sizeof(struct broadcast_message));
    broadcast_send(&broadcast);
    seqno++;
  }

  PROCESS_END();
}

PROCESS_THREAD(make_sensed_data_process, ev, data){
    int pulse;
    int oxygen;
    int temp;
    static struct etimer timer;
    PROCESS_BEGIN();
    etimer_set(&timer, CLOCK_SECOND + random_rand() % (CLOCK_SECOND * 9) + CLOCK_SECOND);
    while ((1))
    {
        PROCESS_WAIT_EVENT_UNTIL(ev= PROCESS_EVENT_TIMER);//execute every 1~3 seconds.
        pulse = (40+ random_rand() % 80); //Arbitrary setting to produce a normal range of sensing values
        oxygen = (85+ random_rand() % 12);
        temp = (35 + random_rand() % 5);
        if(new_transaction(pulse, oxygen, temp)){//When the transaction array is full of 100
          /*If you make a mining request again while mining, duplicate operations will be huge.
          Multicast here should be a regular function, not a thread.

            //1. Multicast Send a message string"LET'S START MINE!"" */
        
            Msg* msg;
            unicast_open(&uc, 146, &unicast_callbacks);
            msg->msg = "Mining plz";        
            packetbuf_copyfrom(msg, sizeof(Msg));
            addr.u8[0] = 1;//head addr
            addr.u8[1] = 0;
            if(!linkaddr_cmp(&addr, &linkaddr_node_addr)) {
            unicast_send(&uc, &addr);
            /*2. Receive timeframe from head node. //The head node receives the performance of each node and calculates the timeframe.
            3. poew
            4. if winner flag is ture, make a new block
            5. add to chain
            6. resolve_conflicts() //replace to the longest chain
          */
        }
  
        etimer_reset(&timer);
    }
    PROCESS_END();
}