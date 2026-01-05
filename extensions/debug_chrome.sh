#!/bin/bash

# Script để chạy Chrome với logging và test extension

echo "🚀 Starting Chrome with debug logging..."
echo "📝 Logs will be saved to: /tmp/chrome_debug.log"
echo ""
echo "Hướng dẫn:"
echo "1. Chrome sẽ mở với logging enabled"
echo "2. Test extension như bình thường"
echo "3. Nếu Chrome crash, logs sẽ được lưu"
echo "4. Nhấn Ctrl+C để dừng"
echo ""
echo "Press Enter to start..."
read

# Kill existing Chrome instances
killall chrome 2>/dev/null
sleep 2

# Start Chrome with logging
google-chrome \
  --enable-logging \
  --v=1 \
  --log-level=0 \
  --enable-features=NetworkService \
  --disable-features=RendererCodeIntegrity \
  2>&1 | tee /tmp/chrome_debug.log

echo ""
echo "✅ Chrome closed. Check logs at: /tmp/chrome_debug.log"
echo ""
echo "To view logs:"
echo "  cat /tmp/chrome_debug.log | grep -i 'error\|crash\|fatal'"
