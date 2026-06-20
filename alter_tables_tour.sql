USE `BookingTravel`;

ALTER TABLE `tour` 
    ADD COLUMN start_dates Text NULL AFTER is_published;