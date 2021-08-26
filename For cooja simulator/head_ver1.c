#include "contiki.h"
#include "lib/list.h"
#include "lib/memb.h"
#include "net/rime/rime.h"
#include "sys/rtimer.h"
#include "net/rime/collect.h"
#include "net/netstack.h"


#include <stdio.h> /* For printf() */
#include <stdint.h>
#include <string.h>
#include <stddef.h>

#define SIZEOFBLOCK = 3448;
typedef struct msg {char * msg; int num;}Msg;

typedef struct results{//Pow 결과 proof와 difficulty를 반환하기 위한 구조체
    int proof;
    int difficulty;
}PoWEresult;

static struct unicast_conn uc1;
static struct collect_conn cc;

static void
recv(const linkaddr_t *originator, uint8_t seqno, uint8_t hops)
{
  char* collectms = (char*)packetbuf_dataptr();

  printf("Sink got message from %d.%d, seqno %d, hops %d: len %d '%s'\n",
         originator->u8[0], originator->u8[1],
         seqno, hops,
         packetbuf_datalen(),
        // (char *)packetbuf_dataptr());
        colms);
        if (collectms[0] == 'M')
        {
            Msg* msg;
            unicast_open(&uc, 146, &unicast_callbacks);

            msg->msg = "Your time frame is";     
            msg->num = 60;//TODO : timeframe calculating   
            packetbuf_copyfrom(msg, sizeof(Msg));
            addr.u8[0] = originator->u8[0];//head addr
            addr.u8[1] = originator->u8[1];
            if(!linkaddr_cmp(&addr, &linkaddr_node_addr)) {
            unicast_send(&uc, &addr);
   
        }
        
}

static const struct collect_callbacks callbacks = { recv };


typedef struct msg {char * msg;}Msg;

static void
recv_uc(struct unicast_conn *c, const linkaddr_t *from)
{
        Msg* msg;
        msg = packetbuf_dataptr();
  printf("unicast message received from %d.%d\n%s\n",
         from->u8[0], from->u8[1], msg->msg);

// if(msg->msg[0]== "M")
//         {
//         msg->msg = "ok";        
//         packetbuf_copyfrom(msg, sizeof(Msg));
//         unicast_send(&c, &from);
//         }
unicast_close(&c);
}

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

//----neighbor------
struct broadcast_message {
  uint8_t seqno;
};

struct unicast_message {
  uint8_t type;
  char * msms;
};

enum {
  UNICAST_TYPE_PING,
  UNICAST_TYPE_PONG
};

struct neighbor{
  struct neighbor *next;
  linkaddr_t addr;

  uint16_t last_rssi, last_lqi;
  uint8_t last_seqno;
  uint32_t avg_seqno_gap;
  //this value will save neighbor node's PoW result
  PoWEresult result = {0, 9999};
}

#define MAX_NEIGHBORS 16
MEMB(neighbors_memb, struct neighbor, MAX_NEIGHBORS);
LIST(neighbors_list);
static struct broadcast_conn broadcast;
static struct unicast_conn unicast;
#define SEQNO_EWMA_UNITY 0x100
#define SEQNO_EWMA_ALPHA 0x040

//not complete
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
//--------Broadcast------
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

PROCESS(main_process, "메인");
AUTOSTART_PROCESSES(&mian_process);

PROCESS_THREAD(main_process, ev, data)
{
  PROCESS_BEGIN();
  //모든 주변 노드에 대해 각기 다른 포트로 소켓통신을 연다. sink를 쓸 수도 있는것 같지만 시간문제로 임기응변
  static linkaddr_t oldparent;
  const linkaddr_t *parent;
  collect_open(&cc, 130, COLLECT_ROUTER, &callbacks);

  if(linkaddr_node_addr.u8[0] == 1 && linkaddr_node_addr.u8[1] == 0)
  {
    printf("I am sink\n"); collect_set_sink(&cc, 1);//Sets the node as sink. Note that we are setting node 1.0 as the sink here.

  }
      packetbuf_clear();
      packetbuf_set_datalen(sprintf(packetbuf_dataptr(), "%s", "Hello") + 1);
      collect_send(&cc, 15);

    }

  while (1)
  {
    //반복
       parent = collect_parent(&tc);
      if(!linkaddr_cmp(parent, &oldparent)) {
        if(!linkaddr_cmp(&oldparent, &linkaddr_null)) {
          printf("#L %d 0\n", oldparent.u8[0]);
        }
        if(!linkaddr_cmp(parent, &linkaddr_null)) {
          printf("#L %d 1\n", parent->u8[0]);
        }
        linkaddr_copy(&oldparent, parent);
      
  }
  
  
  PROCESS_END();
}