// Step 1: React + Vite + TypeScript 프로젝트 설정
// Vite로 React 프로젝트를 생성하고 TypeScript를 설정합니다.
// 아래 명령어를 사용:
// npm create vite@latest my-project --template react-ts
// cd my-project
// npm install

// Step 2: 웹캠 접속 및 QR 코드 스캔 구현
import React, { useEffect, useRef, useState } from 'react';
import jsQR from 'jsqr';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const QRScanner: React.FC = () => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [qrData, setQrData] = useState<string | null>(null);

    useEffect(() => {
        const startCamera = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    videoRef.current.play();
                }
            } catch (err) {
                console.error('Error accessing webcam:', err);
            }
        };

        startCamera();
    }, []);

    useEffect(() => {
        const scanQRCode = () => {
            if (!canvasRef.current || !videoRef.current) return;

            const canvas = canvasRef.current;
            const video = videoRef.current;
            const context = canvas.getContext('2d');

            if (context) {
                canvas.width = video.videoWidth || 640; // Default width to avoid errors
                canvas.height = video.videoHeight || 480; // Default height to avoid errors

                if (canvas.width > 0 && canvas.height > 0) {
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);

                    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                    const code = jsQR(imageData.data, imageData.width, imageData.height);

                    if (code) {
                        setQrData(code.data);
                        window.setTimeout(() =>requestAnimationFrame(scanQRCode), 500)
                    } else {
                        requestAnimationFrame(scanQRCode);
                    }
                }
            }
        };

        if (videoRef.current) {
            videoRef.current.addEventListener('play', scanQRCode);
        }

        return () => {
            if (videoRef.current) {
                videoRef.current.removeEventListener('play', scanQRCode);
            }
        };
    }, []);

    const sendQrDataToServer = async (data: string) => {
        try {
            const response = await fetch(`/api/qr/${data}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ qrData: data }),
            });

            const result = await response.json();
            console.log('Server response:', result);
            toast(result.message)
        } catch (err) {
            console.error('Error sending QR data:', err);
        }
    };

    useEffect(() => {
        if (qrData) {
            sendQrDataToServer(qrData);
        }
    }, [qrData]);

    return (
        <div style={{
            display: 'flex',
            width: '80vw',
            height: '80vh',
            overflow: 'hidden',

            padding: '10vh',

            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',

        }}>
            <video ref={videoRef} style={{ width: '100%' }} />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            {/*{qrData && <p>QR Data: {qrData}</p>}*/}
            <ToastContainer />
        </div>
    );
};

export default QRScanner;

// Step 4: 서버에 QR 데이터를 전송하고 응답 처리
// 서버의 `/api/verify-qr` 엔드포인트는 QR 데이터를 검증하고 결과를 반환합니다.
