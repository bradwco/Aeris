import React, { useRef, useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  Easing,
  TouchableOpacity,
} from "react-native";
import Slider from '@react-native-community/slider';
import Header from '../components/Header';
import { handleJoystickUp, handleJoystickDown, handleJoystickLeft, handleJoystickRight, handleSliderChange } from '../util';

export default function Settings({ navigation }) {
  const fan = require("../assets/fan_spinning_centered.png");
  const { height: windowHeight } = Dimensions.get("window");
  const topOffset = Math.round(windowHeight * 0.08);

  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(opacity, { toValue: 1, duration: 300, useNativeDriver: true }).start();
  }, []);

  const navigateWithFade = (screen) => {
    Animated.timing(opacity, { toValue: 0, duration: 250, useNativeDriver: true }).start(() => {
      navigation.navigate(screen);
    });
  };

  const spin = useRef(new Animated.Value(0)).current;

  const [speed, setSpeed] = useState(1000);

  const speedRef = useRef(speed);
  useEffect(() => { speedRef.current = speed; }, [speed]);

  useEffect(() => {
    let rafId = null;
    let last = Date.now();
    let angle = 0;

    const tick = () => {
      const now = Date.now();
      const dt = now - last;
      last = now;
      const curSpeed = speedRef.current;
      if (curSpeed > 0) {
        const deltaDeg = (dt / curSpeed) * 360;
        angle = (angle + deltaDeg) % 360;
        spin.setValue(angle / 360);
      }
      rafId = requestAnimationFrame(tick);
    };

    rafId = requestAnimationFrame(tick);
    return () => { if (rafId) cancelAnimationFrame(rafId); };
  }, []);

  const spinInterpolate = spin.interpolate({
    inputRange: [0, 1],
    outputRange: ["0deg", "360deg"],
  });

  const sliderValue = 100 - ((speed - 500) / (5000 - 500)) * 100;

  const handleDirectionPress = (direction) => {
    switch (direction) {
      case "up":
        handleJoystickUp();
        break;
      case "down":
        handleJoystickDown();
        break;
      case "left":
        handleJoystickLeft();
        break;
      case "right":
        handleJoystickRight();
        break;
      default:
        break;
    }
  };

  const handleSliderPress = () => {
    handleSliderChange(speed);
  };

  return (
    <Animated.View style={[styles.container, { paddingTop: topOffset, opacity }]}>
      <Header navigation={navigation} currentScreen="Settings" navigateWithFade={navigateWithFade} />

      <Text style={styles.screenTitle}>Airflow Control</Text>

      <View style={styles.fanWrap}>
        <Animated.Image source={fan} style={[styles.fanImage, { transform: [{ rotate: spinInterpolate }] }]} resizeMode="contain" />
      </View>

      <Slider
        style={styles.slider}
        minimumValue={0}
        maximumValue={100}
        value={sliderValue}
        onValueChange={(value) => {
          const adjustedSpeed = 5000 - (value / 100) * 4500;
          setSpeed(Math.max(0, adjustedSpeed));
          handleSliderChange(adjustedSpeed);
        }}
        minimumTrackTintColor="#FFFFFF"
        maximumTrackTintColor="#000000"
      />
      <Text style={styles.sliderValue}>Speed: {Math.round(sliderValue)}%</Text>

      <View style={styles.joystickContainer}>
        <TouchableOpacity
          style={styles.joystickButton}
          onPress={() => handleDirectionPress("up")}
        >
          <Text style={styles.joystickText}>↑</Text>
        </TouchableOpacity>
        <View style={styles.horizontalRow}>
          <TouchableOpacity
            style={styles.joystickButton}
            onPress={() => handleDirectionPress("left")}
          >
            <Text style={styles.joystickText}>←</Text>
          </TouchableOpacity>
          <View style={styles.centerSpacer} />
          <TouchableOpacity
            style={styles.joystickButton}
            onPress={() => handleDirectionPress("right")}
          >
            <Text style={styles.joystickText}>→</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity
          style={styles.joystickButton}
          onPress={() => handleDirectionPress("down")}
        >
          <Text style={styles.joystickText}>↓</Text>
        </TouchableOpacity>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  screenTitle: { color: '#fff', fontSize: 30, textAlign: 'center', marginTop: 8, marginBottom: 12, fontWeight: '600' },
  fanWrap: { alignItems: 'center', justifyContent: 'center', height: 300 },
  fanImage: { width: 320, height: 280 },
  slider: { width: '80%', alignSelf: 'center', marginTop: 12 },
  sliderValue: { color: '#fff', fontSize: 18, textAlign: 'center', marginTop: 12 },
  joystickContainer: {
    marginTop: 30,
    paddingBottom: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  horizontalRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 10,
  },
  centerSpacer: {
    width: 30,
  },
  joystickButton: {
    width: 50,
    height: 50,
    backgroundColor: '#333',
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    margin: 5,
  },
  joystickText: { color: '#fff', fontSize: 20 },
});
