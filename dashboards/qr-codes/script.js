document.getElementById('generate-btn').addEventListener('click', () => {
  const qrText = document.getElementById('qr-text').value;
  const qrType = document.getElementById('qr-type').value;

  let qrData = '';

  if (qrText.trim() === '') {
    alert('Please enter the required information!');
    return;
  }

  // Handle different QR code types
  if (qrType === 'text') {
    qrData = qrText;
  } else if (qrType === 'phone') {
    qrData = `tel:${qrText}`;
  } else if (qrType === 'location') {
    const [latitude, longitude] = qrText.split(',').map(coord => coord.trim());
    if (!latitude || !longitude || isNaN(latitude) || isNaN(longitude)) {
      alert('Please enter valid latitude and longitude in the format: latitude,longitude');
      return;
    }
    qrData = `geo:${latitude},${longitude}`;
  }

  // Generate the QR code
  const qr = new QRious({
    element: document.getElementById('qr-code'),
    value: qrData,
    size: 200, // QR code size in pixels
  });

  // Enable the download button
  const downloadBtn = document.getElementById('download-btn');
  downloadBtn.disabled = false;

  // Add click event for downloading the QR code
  downloadBtn.addEventListener('click', () => {
    const canvas = document.getElementById('qr-code');
    const dataURL = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.href = dataURL;
    link.download = 'qr-code.png';
    link.click();
  });
});
