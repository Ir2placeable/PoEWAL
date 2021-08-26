#include "contiki.h"
#include "sys/rtimer.h"

#include "random.h"
#include <stddef.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>


typedef struct transaction
{
    int pulse;
    int oxygen;
    int temp;
}Transaction;

Transaction current_transactions[100];//the struct array to collect the sensor datas for make a block.
int lastOfctran = -1;

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
        //printf("Transaction will be added to Block %d\n", lastOfVector+1); <this part for whole code.
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
PROCESS(make_sensed_data_process, "Randomly create transaction variables at regular intervals");
AUTOSTART_PROCESSES(&make_sensed_data_process);
PROCESS_THREAD(make_sensed_data_process, ev, data){
    int pulse;
    int oxygen;
    int temp;
    static struct etimer timer;
    PROCESS_BEGIN();
    etimer_set(&timer,CLOCK_SECOND+ random_rand() % (CLOCK_SECOND * 9) + CLOCK_SECOND);
    while ((1))
    {
        PROCESS_WAIT_EVENT_UNTIL(ev= PROCESS_EVENT_TIMER);//Run every 1-3 seconds
        pulse = (40+ random_rand() % 80);
        oxygen =(85+ random_rand() % 12);
        temp = (35 + random_rand() % 5);
        new_transaction(pulse, oxygen, temp);
        etimer_reset(&timer);
    }
    PROCESS_END();
}



