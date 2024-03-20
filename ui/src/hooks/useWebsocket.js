import { io } from "socket.io-client";


export const useWebsocket = (url) => {
    const socket = new io(url);

    socket.on('connect', function () {
        console.log('connected')
    });

    return socket;
}
