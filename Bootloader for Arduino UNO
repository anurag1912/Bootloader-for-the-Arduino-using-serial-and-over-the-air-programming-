/*
 * Bootloader.c
 *
 * Created: 12/2/2015 12:23:05 AM
 *  
 */ 


#include<avr/io.h>
#include<avr/wdt.h>
#include<avr/boot.h>
#include <inttypes.h>
#include<avr/interrupt.h>
void boot_program_page (uint32_t page, uint8_t *buf);			//Function to write a temporary page buffer and enable SPM
void boot_func(void);											//Bootloader code that implements the protocol
void uart_init(unsigned char);									//Initialize UART
int main(void)
{	unsigned char ch = MCUSR;									//MCU Status register that determines what type of reset occured
	MCUSR=0;
	cli();
	wdt_reset();
	WDTCSR |= (1<<WDCE) | (1<<WDE);
	WDTCSR = 0x00;
								   
	if((ch & (1<<EXTRF)))				//If external reset 
	{	uart_init(1);
		boot_func();			//if completes successfully, then jump to application space!!!
		asm ("jmp 0x0000");
	}	   
	 
	else if((ch & (1<<WDRF))){					//If watch dog reset i.e. software reset 
		
		uart_init(8);
		boot_func();			//if completes successfully, then jump to application space!!!
		asm ("jmp 0x0000");
	} 
	else{sei();					//pressed external reset button
		asm ("jmp 0x0000");

	}
	while(1);
	return 0;
}
void uart_init(unsigned char ch)
{
	
	/*-------------------------------
	UART Init.
	----------------------------------*/
	UCSR0B = UCSR0B | (1<<RXEN0) | (1<<TXEN0);									//Enable RX and TX
	UCSR0C = UCSR0C | (1<<UCSZ01) | (1<<UCSZ00);								//1 stop bit, no parity , data = 8 bits
	UBRR0 = ch;																	//Baud Rate = 0.5Mbps																
	/*--------------------------------------
	End Init.
	---------------------------------------*/
}
void boot_program_page (uint32_t page, uint8_t *buf)
{
	uint16_t i;
	uint8_t sreg;
	// Disable interrupts.
	sreg = SREG;
	cli();
	eeprom_busy_wait ();
	boot_page_erase (page);
	boot_spm_busy_wait (); // Wait until the memory is erased.
	for (i=0; i<SPM_PAGESIZE; i+=2)
	{
		// Set up little-endian word.
		uint16_t w = *buf++;
		w += (*buf++) << 8;
		boot_page_fill (page + i, w);
	}
	boot_page_write (page); // Store buffer in flash page.
	boot_spm_busy_wait(); // Wait until the memory is written.
	// Reenable RWW-section again. We need this if we want to jump back
	// to the application after bootloading.
	boot_rww_enable ();
	// Re-enable interrupts (if they were ever enabled).
	SREG = sreg;
}


void boot_func(void){
	
/*
Protocol---On reset send 'K' , the external device will respond with 'S' and device will wait for block of 128 bytes
after 128 bytes have been transmitted, external device will respond with either 'S' to indicate next block or will end
communication with 'F' (external reset) or 'X' (software reset). If error occurs an 'E' is transmitted and both devices are synchronized.
Time-out on both sides is approx 4 secs after which the devices are disengaged.
*/
#define RESETTIMER	flag =0; TIFR1 |= (1<<OCF1A); TCNT1 =0;
	uint32_t page=0;					
	unsigned char valid='K';
	unsigned char flag=0;
	unsigned char buf[128];				//to store buffer of 128 bytes
	unsigned char byte;
	/*-----------------------------------------------
	Timer Init.
	-------------------------------------------------*/
	TCCR1A = 0;
	TCCR1B = 0;
	OCR1A =	0xFFFF;										//~4 seconds 
	TCCR1B |= (1<<WGM12) | (1<<CS12) | (1<<CS10);
	TIFR1 |= (1<<OCF1A);
	TCNT1 =0;
	/*--------------------------------------------
	End Init.
	---------------------------------------------*/
	
	
	UDR0 = valid;																//Sending 'K'
	RESETTIMER
	
	while((UCSR0A & (1<<RXC0))==0)
	{if((TIFR1 & (1<<OCF1A))!=0)
		{
			flag = 1;						//for time-out
			break;
			
		}
	
	}
	if(flag==0)
	{valid=UDR0;
	if (valid != 'S')
	{valid=0x03;						//Error condition !S
	UDR0 = valid;
	asm ("jmp 0x0000");					//Should be asm jump to application!!!
	}	
	else 
	UDR0=valid;

	}	
	else			
	{TCCR1A = 0;
	TCCR1B = 0;
	OCR1A=0;
	TCNT1=0;
	UCSR0A=32;
	UCSR0B=0;
	UCSR0C=6;
	UBRR0=0;
	asm ("jmp 0x0000");						//Should be asm jump!
	}	
	
	RESETTIMER
	while(valid!='F' && valid!='X')			//If valid is !F or !X
	{	
		
		byte=0;
		while(byte<128)
		{ unsigned char instr=0;
			while((UCSR0A & (1<<RXC0))==0)
			{
				if((TIFR1 & (1<<OCF1A))!=0)
				{
					flag = 1;
					break;
					
				}
				
			}
			if(flag==0)
			{	
				valid = UDR0;
				UDR0 = valid;				//echo
				if(valid>='0' && valid<='9')
				valid = valid - '0';
				else if(valid >='A' && valid<='F')
				valid = (valid -'A') + 10;
				instr = valid;
				
				RESETTIMER
			}
			else
			{
				
				while(1);				//Operation timed out should busy loop as code is not written!!!
			}
			
			
			
			while((UCSR0A & (1<<RXC0))==0)
			{
				if((TIFR1 & (1<<OCF1A))!=0)
				{
					flag = 1;
					break;
					
				}
				
			}
			if(flag==0)
			{	instr = (instr<<4);
				valid = UDR0;
				UDR0 = valid;				//echo
				if(valid>='0' && valid<='9')
				valid = valid - '0';
				else if(valid >='A' && valid<='F')
				valid = (valid -'A') + 10;
				instr+= valid;
				
				
				RESETTIMER
			}
			else
			{
				
				while(1);				//Operation timed out should busy loop as code is not written!!!
			}
			buf[byte] =instr;
			byte++;
			
		}
			
	while((UCSR0A & (1<<RXC0))==0)
	{if((TIFR1 & (1<<OCF1A))!=0)
		{
			flag = 1;
			break;
			
		}
		
	}
	if(flag==0)
	{valid=UDR0;
		UDR0=valid;
		if (valid != 'E')				//i.e valid == 'S'
		{	//Get ready for next block transfer
			
			boot_program_page (page, buf);
			page+=128; 
			
		}
		
		else{
			RESETTIMER
		while((UCSR0A & (1<<RXC0))==0)
		{if((TIFR1 & (1<<OCF1A))!=0)
			{
				flag = 1;
				break;
				
			}
			
		}
		if(flag==0)
		{valid=UDR0;
		UDR0 = valid;
		}		
		else
		while(1);						//busy loop as 'S' was not received
		RESETTIMER
		
		
		}
	}
	else
	while(1);							//Code partially received should busy loop!		
	RESETTIMER	
		
		
	}
	//Code received successfully undo everything!
	TCCR1A = 0;
	TCCR1B = 0;
	OCR1A=0;
	TCNT1=0;
	UCSR0A=32;
	UCSR0B=0;
	UCSR0C=6;
	UBRR0=0;
	
	
	
	


}
