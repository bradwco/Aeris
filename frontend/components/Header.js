import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Image,
  Pressable,
} from "react-native";

export default function Header({ navigation, currentScreen }) {
  const logo = require("../assets/icon.png");

  return (
    <View style={styles.header}>
      <View style={styles.brandRowTop}>
        <Image source={logo} style={styles.logo} />
        <Text style={styles.appTitle}>Aeris</Text>
      </View>

      <View style={styles.navRow}>
        <View style={styles.topNav}>
          <Pressable
            onPress={() => navigation.navigate("Home")}
            style={({ pressed }) => [styles.topNavItem, pressed && styles.pressed]}
          >
            <Text style={currentScreen === "Home" ? styles.topNavTextActive : styles.topNavText}>
              Home
            </Text>
          </Pressable>
          <Pressable
            onPress={() => navigation.navigate("Settings")}
            style={({ pressed }) => [styles.topNavItem, pressed && styles.pressed]}
          >
            <Text style={currentScreen === "Settings" ? styles.topNavTextActive : styles.topNavText}>
              Settings
            </Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: 18, paddingBottom: 6 },
  brandRowTop: { flexDirection: "row", alignItems: "center", marginBottom: 6 },
  logo: { width: 34, height: 34, marginRight: 12 },
  appTitle: { color: "#fff", fontSize: 20, fontWeight: "700" },
  navRow: { alignItems: "center", justifyContent: "center" },
  topNav: { flexDirection: "row", alignItems: "center" },
  topNavItem: { paddingHorizontal: 12, paddingVertical: 6, marginHorizontal: 18 },
  topNavText: { color: "#bdbdbd", fontSize: 18 },
  topNavTextActive: { color: "#fff", fontSize: 18, fontWeight: "700" },
  pressed: { opacity: 0.6 },
});
