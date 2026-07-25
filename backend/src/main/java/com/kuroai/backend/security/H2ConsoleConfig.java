package com.kuroai.backend.security;

import org.h2.server.web.JakartaWebServlet;
import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class H2ConsoleConfig {

    @Bean
    public ServletRegistrationBean<JakartaWebServlet> h2ConsoleServletRegistration() {
        ServletRegistrationBean<JakartaWebServlet> registration = new ServletRegistrationBean<>(
                new JakartaWebServlet(), "/h2-console/*");
        // Equivalent to spring.h2.console.settings.web-allow-others=true
        registration.addInitParameter("webAllowOthers", "true");
        return registration;
    }
}
