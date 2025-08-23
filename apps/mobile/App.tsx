import React from 'react';
import { SafeAreaView, Text, Button } from 'react-native';

export default function App(){
  const [s,setS] = React.useState('disconnected');
  const WS_URL = (process.env.EXPO_PUBLIC_WS_URL || 'ws://localhost:8000/ws/audio') as string;
  return (
    <SafeAreaView style={{flex:1,alignItems:'center',justifyContent:'center'}}>
      <Text>Vakta Mobile Stub — {s}</Text>
      <Button title="Connect" onPress={()=>{
        const ws = new WebSocket(WS_URL);
        ws.onopen = ()=>{ setS('connected'); ws.send(JSON.stringify({type:'start'})); };
        ws.onmessage = (e)=>console.log('msg', e.data);
        ws.onclose = ()=>setS('disconnected');
      }} />
    </SafeAreaView>
  );
}
