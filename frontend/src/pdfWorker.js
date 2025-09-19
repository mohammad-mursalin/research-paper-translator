// Tell pdfjs where to find its worker
import { GlobalWorkerOptions } from 'pdfjs-dist/build/pdf';
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
GlobalWorkerOptions.workerSrc = workerUrl;