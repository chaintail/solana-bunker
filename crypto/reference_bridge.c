/* Thin parameter/length wrapper around the pinned independent C reference. */
#include <string.h>
#include <stdlib.h>
#include "params.h"
#include "xmss_core.h"
static int params(xmss_params *p) { return xmss_parse_oid(p,1); }
int bunker_keygen(unsigned char *pk,unsigned char *sk,const unsigned char *seed) {
 xmss_params p; if(params(&p))return -3; unsigned char s[96]; memcpy(s,seed,96);
 return xmssmt_core_seed_keypair(&p,pk,sk,s);
}
int bunker_sign_at(unsigned char *sig,const unsigned char *sk0,unsigned int idx,const unsigned char *msg,unsigned long long len) {
 if(idx>=1024 || len>4096)return -3;
 xmss_params p; if(params(&p))return -3;
 unsigned char sk[132]; memcpy(sk,sk0,132);
 sk[0]=idx>>24;sk[1]=idx>>16;sk[2]=idx>>8;sk[3]=idx;
 unsigned char *sm=malloc(2500+len);unsigned long long smlen=0;
 int r=xmss_core_sign(&p,sk,sm,&smlen,msg,len);
 if(!r && smlen==2500+len)memcpy(sig,sm,2500);else if(!r)r=-4;
 free(sm);memset(sk,0,sizeof(sk));return r;
}
int bunker_verify(const unsigned char *pk,const unsigned char *sig,const unsigned char *msg,unsigned long long len) {
 if(len>4096)return -3;
 xmss_params p; if(params(&p))return -3;
 unsigned char *sm=malloc(2500+len),*out=malloc(2500+len); unsigned long long outlen=0;
 memcpy(sm,sig,2500);memcpy(sm+2500,msg,len);
 int r=xmss_core_sign_open(&p,out,&outlen,sm,2500+len,pk);
 if(!r && (outlen!=len||memcmp(out,msg,len)))r=-4;
 free(sm);free(out);return r;
}
